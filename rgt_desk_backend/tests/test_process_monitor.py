import unittest
from unittest.mock import Mock, patch

import api
from models import StartProcessRequest, StopProcessRequest
from process_monitor import ProcessMonitor


class ProcessMonitorTests(unittest.TestCase):
    def setUp(self):
        self.monitor = ProcessMonitor()
        self.windows = set()
        self.node = Mock()
        self.get_windows = patch(
            "process_monitor.tmux.get_windows", side_effect=lambda: list(self.windows)
        ).start()
        self.start_process = patch(
            "process_monitor.tmux.start_process",
            side_effect=lambda name, command: self.windows.add(name),
        ).start()
        self.stop_process = patch(
            "process_monitor.tmux.stop_process", side_effect=self.windows.discard
        ).start()
        self.addCleanup(patch.stopall)

    def observe(self, *nodes):
        self.node.get_node_names_and_namespaces.return_value = list(nodes)
        self.monitor._update_status(self.node)
        return self.monitor.get_status()

    def test_idle_ignores_external_nodes(self):
        nodes = [(name, "/") for name in self.monitor.status]
        nodes += [("ur_robot_manager", "/ur20"), ("ynx_robot_manager", "/nex10")]
        self.assertTrue(all(s == "stopped" for s in self.observe(*nodes).values()))

    def test_start_is_immediate_and_waits_for_first_node(self):
        self.monitor.start_process("rgt_manager", "launch")
        self.assertEqual(self.monitor.get_status()["rgt_manager"], "started")
        for _ in range(3):
            self.assertEqual(self.observe()["rgt_manager"], "started")
        # No startup timeout is implied, even if the launching shell exits.
        self.windows.clear()
        self.assertEqual(self.observe()["rgt_manager"], "started")

    def test_each_process_tracks_node_appearance_loss_and_recovery(self):
        for name in self.monitor.status:
            with self.subTest(process=name):
                node_name = self.monitor.NODE_NAMES.get(name, name)
                self.monitor.start_process(name, "launch")
                self.assertEqual(self.observe((node_name, "/cell"))[name], "running")
                self.assertEqual(self.observe()[name], "error")
                self.assertEqual(self.observe()[name], "error")
                self.assertEqual(self.observe((node_name, "/cell"))[name], "running")

    def test_node_match_is_exact_and_does_not_match_namespace(self):
        self.monitor.start_process("rgt_manager", "launch")
        states = self.observe(
            ("rgt_manager_helper", "/"),
            ("other_node", "/rgt_manager"),
        )
        self.assertEqual(states["rgt_manager"], "started")

    def test_robots_require_manager_nodes(self):
        for name in ("ur20", "nex10"):
            self.monitor.start_process(name, "launch")
        states = self.observe(
            ("ur20", "/"), ("nex10", "/"),
            ("controller_manager", "/nex10"),
            ("ur_robot_manager_helper", "/ur20"),
        )
        self.assertEqual(states["ur20"], "started")
        self.assertEqual(states["nex10"], "started")
        states = self.observe(
            ("ur_robot_manager", "/ur20"), ("ynx_robot_manager", "/nex10")
        )
        self.assertEqual(states["ur20"], "running")
        self.assertEqual(states["nex10"], "running")

    def test_window_loss_does_not_hide_node_lifecycle(self):
        self.monitor.start_process("rgt_manager", "launch")
        self.observe(("rgt_manager", "/"))
        self.windows.clear()
        self.assertEqual(self.observe(("rgt_manager", "/"))["rgt_manager"], "running")
        self.assertEqual(self.observe()["rgt_manager"], "error")

    def test_explicit_stop_returns_idle_despite_stale_node(self):
        for nodes in ([], [("rgt_manager", "/")]):
            with self.subTest(nodes=nodes):
                self.monitor.start_process("rgt_manager", "launch")
                self.observe(*nodes)
                self.monitor.stop_process("rgt_manager")
                self.assertEqual(self.monitor.get_status()["rgt_manager"], "stopped")
                self.assertEqual(self.observe(("rgt_manager", "/"))["rgt_manager"], "stopped")
                self.assertEqual(self.observe()["rgt_manager"], "stopped")

    def test_new_launch_after_error_resets_startup_history(self):
        self.monitor.start_process("rgt_manager", "launch")
        self.observe(("rgt_manager", "/"))
        self.observe()
        self.monitor.stop_process("rgt_manager")
        self.monitor.start_process("rgt_manager", "launch")
        self.assertEqual(self.observe()["rgt_manager"], "started")

    def test_repeated_start_does_not_reset_existing_process(self):
        self.monitor.start_process("rgt_manager", "launch")
        self.observe(("rgt_manager", "/"))
        self.monitor.start_process("rgt_manager", "launch")
        self.assertEqual(self.monitor.get_status()["rgt_manager"], "running")
        self.observe()
        self.monitor.start_process("rgt_manager", "launch")
        self.assertEqual(self.monitor.get_status()["rgt_manager"], "error")
        self.windows.clear()
        self.monitor.start_process("rgt_manager", "launch")
        self.assertEqual(self.observe()["rgt_manager"], "started")

    def test_adopts_existing_tmux_windows(self):
        self.windows.update(["rgt_manager", "ur20"])
        states = self.observe(("ur_robot_manager", "/ur20"))
        self.assertEqual(states["ur20"], "running")
        self.assertEqual(states["rgt_manager"], "started")

    def test_failed_tmux_actions_do_not_change_state(self):
        self.start_process.side_effect = RuntimeError("launch failed")
        with self.assertRaises(RuntimeError):
            self.monitor.start_process("rgt_manager", "launch")
        self.assertEqual(self.monitor.get_status()["rgt_manager"], "stopped")
        self.windows.add("rgt_manager")
        self.observe(("rgt_manager", "/"))
        self.stop_process.side_effect = RuntimeError("stop failed")
        with self.assertRaises(RuntimeError):
            self.monitor.stop_process("rgt_manager")
        self.assertEqual(self.monitor.get_status()["rgt_manager"], "running")

    def test_status_returns_snapshot(self):
        snapshot = self.monitor.get_status()
        self.monitor.start_process("rgt_manager", "launch")
        self.assertEqual(snapshot["rgt_manager"], "stopped")

    def test_api_start_stop_updates_monitor(self):
        with patch.object(api, "process_monitor", self.monitor):
            self.assertEqual(
                api.start_process(StartProcessRequest(name="rgt_manager")),
                {"name": "rgt_manager", "status": "started"},
            )
            self.start_process.assert_called_once_with(
                "rgt_manager", "../process_scripts/rgt_manager.sh"
            )
            self.assertEqual(api.get_status()["rgt_manager"], "started")
            self.observe(("rgt_manager", "/"))
            self.assertEqual(
                api.stop_process(StopProcessRequest(name="rgt_manager")),
                {"name": "rgt_manager", "status": "stopped"},
            )
            self.stop_process.assert_called_once_with("rgt_manager")
            self.assertEqual(api.get_status()["rgt_manager"], "stopped")


if __name__ == "__main__":
    unittest.main()
