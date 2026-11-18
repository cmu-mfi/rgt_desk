import os
import shlex
import shutil
import sys
import time
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi import HTTPException
import libtmux

import api
import tmux
from models import CancelServiceRequest, RunServiceRequest
from service_monitor import ServiceBusyError, ServiceMonitor


@unittest.skipUnless(shutil.which("tmux"), "tmux is required")
class ServiceMonitorTests(unittest.TestCase):
    """Real tmux lifecycle checks on a private socket; no ROS calls or robots."""

    def setUp(self):
        self.server = libtmux.Server(socket_name=f"rgt-desk-test-{uuid.uuid4().hex}")
        self.addCleanup(self.server.kill)
        patcher = patch.object(tmux, "tmux_server", self.server)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.monitor = ServiceMonitor()

    def wait_for(self, expected, name="home"):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status = self.monitor.get_status()[name]
            if status == expected:
                return
            time.sleep(0.05)
        self.fail(f"Expected {expected}, got {status}; logs: {self.monitor.get_logs(100)[name]}")

    def python_command(self, code):
        return f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"

    def test_success_failure_logs_and_restart_adoption(self):
        self.assertEqual(self.monitor.get_status()["home"], "idle")
        self.monitor.execute("home", "printf 'service output\\n'")
        self.wait_for("idle")
        self.assertEqual(self.monitor.get_logs(100)["home"], [])
        self.assertNotIn("service-home", tmux.get_windows())
        restarted = ServiceMonitor()
        self.assertEqual(restarted.get_status()["home"], "idle")
        self.assertEqual(restarted.get_logs(100)["home"], [])
        self.monitor.execute("home", "printf 'failure output\\n' >&2; exit 7")
        self.wait_for("idle")
        output = self.monitor.get_logs(100)["home"]
        self.assertEqual(output, [])
        self.assertNotIn("service output", output)
        self.assertNotIn("service-home", tmux.get_windows())

    def test_background_cleanup_without_browser_polling(self):
        self.monitor.execute("home", "echo background-output")
        deadline = time.monotonic() + 5
        while "service-home" in tmux.get_windows():
            if time.monotonic() >= deadline:
                self.fail("Completed service window was not removed")
            time.sleep(0.05)
        self.assertEqual(self.monitor.get_logs(100)["home"], [])

    def test_service_uses_backend_environment_cwd_and_shell_quoting(self):
        # Start tmux before setting the variable, as on a host with an older
        # tmux server that has not sourced the backend's ROS overlay.
        tmux.get_main_session()
        value = "spaces ' quotes; $(literal)"
        with patch.dict(os.environ, {"RGT_DESK_SERVICE_TEST": value}):
            self.monitor.execute(
                "home", 'printf "%s\\n" "$RGT_DESK_SERVICE_TEST"; pwd; exec sleep 60'
            )
        self.wait_for_output(value)
        output = self.monitor.get_logs(100)["home"]
        self.assertIn(value, output)
        self.assertIn(os.getcwd(), output)

    def test_immediate_exits_keep_status_when_repeated(self):
        # Exercise the race between launching a very short script and tmux
        # closing its window, including repeated executions.
        for _ in range(20):
            self.monitor.execute("home", "exit 0")
            self.wait_for("idle")
            self.monitor.execute("home", "exit 7")
            self.wait_for("idle")

    def test_active_call_is_adopted_and_duplicate_rejected(self):
        self.monitor.execute("home", "sleep 60")
        restarted = ServiceMonitor()
        self.assertEqual(restarted.get_status()["home"], "executing")
        with self.assertRaises(ServiceBusyError):
            restarted.execute("home", "echo duplicate")
        self.assertEqual(restarted.cancel("home"), "idle")
        self.assertEqual(restarted.get_status()["home"], "idle")

    def test_concurrent_starts_allow_only_one_call(self):
        def execute(_):
            try:
                self.monitor.execute("home", "sleep 60")
                return "started"
            except ServiceBusyError:
                return "busy"
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertCountEqual(list(pool.map(execute, range(2))), ["started", "busy"])

    def test_cancel_deletes_logs_and_allows_rerun(self):
        self.monitor.execute("home", "printf 'waiting\\n'; exec sleep 60")
        self.wait_for_output("waiting")
        self.assertEqual(self.monitor.cancel("home"), "idle")
        self.assertNotIn("service-home", tmux.get_windows())
        self.assertEqual(self.monitor.get_logs(100)["home"], [])
        self.assertEqual(ServiceMonitor().get_status()["home"], "idle")
        self.monitor.execute("home", "echo rerun")
        self.wait_for("idle")
        self.assertEqual(self.monitor.get_logs(100)["home"], [])
        self.assertNotIn("waiting", self.monitor.get_logs(100)["home"])

    def wait_for_output(self, text):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if text in self.monitor.get_logs(100)["home"]:
                return
            time.sleep(0.05)
        self.fail(f"Missing terminal output: {text}")

    def test_force_cancel_kills_unresponsive_client_and_deletes_output(self):
        command = self.python_command(
            "import os, signal, time; signal.signal(signal.SIGINT, signal.SIG_IGN); "
            "print('client_pid=' + str(os.getpid()), flush=True); "
            "print('ignoring interrupt', flush=True); time.sleep(60)"
        )
        self.monitor.execute("home", f"exec {command}")
        self.wait_for_output("ignoring interrupt")
        pid = next(int(line.split("=", 1)[1]) for line in self.monitor.get_logs(100)["home"]
                   if line.startswith("client_pid="))
        self.assertEqual(self.monitor.cancel("home"), "idle")
        self.assertEqual(self.monitor.get_status()["home"], "idle")
        self.assertEqual(self.monitor.get_logs(100)["home"], [])
        self.assertNotIn("service-home", tmux.get_windows())
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            self.fail("Cancelled client is still alive")

    def test_cancel_idle_call_is_noop(self):
        self.assertEqual(self.monitor.cancel("home"), "idle")
        self.monitor.execute("home", "exit 3")
        self.wait_for("idle")
        self.assertEqual(self.monitor.cancel("home"), "idle")

    def test_removed_window_is_idle_and_process_windows_are_separate(self):
        tmux.start_process("home", "echo process")
        self.monitor.execute("home", "sleep 60")
        tmux.get_main_session().windows.get(window_name="service-home").kill()
        self.assertEqual(self.monitor.get_status()["home"], "idle")
        self.assertIn("home", tmux.get_windows())

    def test_api_start_status_logs_cancel_and_validation(self):
        with patch.object(api, "service_monitor", self.monitor), patch.object(
            api, "build_command", return_value="printf 'api output\\n'; exec sleep 60"
        ):
            self.assertEqual(api.execute_service(RunServiceRequest(name="home")),
                             {"name": "home", "status": "executing"})
            with self.assertRaises(HTTPException) as raised:
                api.execute_service(RunServiceRequest(name="home"))
            self.assertEqual(raised.exception.status_code, 409)
            self.wait_for_output("api output")
            self.assertEqual(api.get_service_status()["home"], "executing")
            self.assertIn("api output", api.get_service_logs(100)["home"])
            self.assertEqual(api.cancel_service(CancelServiceRequest(name="home")),
                             {"name": "home", "status": "idle"})
        for request in (
            lambda: api.execute_service(RunServiceRequest(name="unknown")),
            lambda: api.cancel_service(CancelServiceRequest(name="unknown")),
            lambda: api.execute_service(RunServiceRequest(name="home")),
        ):
            with self.assertRaises(HTTPException) as raised:
                request()
            self.assertIn(raised.exception.status_code, (400, 404))


if __name__ == "__main__":
    unittest.main()
