import time
import unittest
import uuid
from unittest.mock import Mock, patch

import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool

import api
import process_config
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
                node_name = process_config.process_node_name(name)
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

    def test_configured_node_name_overrides_process_name(self):
        with patch.dict(
            process_config._PROCESS_COMMANDS,
            {"rgt_manager": {"node_name": "custom_manager"}},
        ):
            self.monitor.start_process("rgt_manager", "launch")
            self.assertEqual(self.observe(("rgt_manager", "/"))["rgt_manager"], "started")
            self.assertEqual(
                self.observe(("custom_manager_helper", "/custom_manager"))["rgt_manager"],
                "started",
            )
            self.assertEqual(self.observe(("custom_manager", "/cell"))["rgt_manager"], "running")
            self.assertEqual(self.observe()["rgt_manager"], "error")
            self.assertEqual(self.observe(("custom_manager", "/cell"))["rgt_manager"], "running")

    def test_missing_node_name_defaults_to_process_name(self):
        with patch.dict(process_config._PROCESS_COMMANDS, {"rgt_manager": {}}):
            self.monitor.start_process("rgt_manager", "launch")
            self.assertEqual(self.observe(("rgt_manager", "/cell"))["rgt_manager"], "running")

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

    def test_robot_readiness_loss_and_recovery(self):
        nodes = [("ur_robot_manager", "/ur20"), ("ynx_robot_manager", "/nex10")]
        for name in ("ur20", "nex10"):
            self.monitor.start_process(name, "launch")
        for name in ("ur20", "nex10"):
            with self.subTest(robot=name):
                other = "nex10" if name == "ur20" else "ur20"
                self.assertEqual(self.observe(*nodes)[name], "running")
                self.monitor._readiness_callback(name, Bool(data=False))
                for _ in range(3):
                    states = self.observe(*nodes)
                    self.assertEqual(states[name], "error")
                    self.assertEqual(states[other], "running")
                self.monitor._readiness_callback(name, Bool(data=True))
                self.assertEqual(self.observe(*nodes)[name], "running")

    def test_initial_false_readiness_and_adoption(self):
        for name, node in (("ur20", "ur_robot_manager"), ("nex10", "ynx_robot_manager")):
            with self.subTest(robot=name):
                self.monitor._readiness_callback(name, Bool(data=False))
                self.windows.add(name)
                self.assertEqual(self.observe((node, f"/{name}"))[name], "error")

    def test_true_readiness_does_not_hide_missing_manager(self):
        self.monitor.start_process("ur20", "launch")
        self.monitor._readiness_callback("ur20", Bool(data=True))
        self.assertEqual(self.observe()["ur20"], "started")
        self.assertEqual(self.observe(("ur_robot_manager", "/ur20"))["ur20"], "running")
        self.assertEqual(self.observe()["ur20"], "error")
        self.monitor._readiness_callback("ur20", Bool(data=True))
        self.assertEqual(self.observe()["ur20"], "error")

    def test_readiness_messages_do_not_override_explicit_stop(self):
        for name, node in (("ur20", "ur_robot_manager"), ("nex10", "ynx_robot_manager")):
            with self.subTest(robot=name):
                self.monitor.start_process(name, "launch")
                self.observe((node, f"/{name}"))
                self.monitor.stop_process(name)
                for ready in (False, True):
                    self.monitor._readiness_callback(name, Bool(data=ready))
                    self.assertEqual(self.observe((node, f"/{name}"))[name], "stopped")

    def test_readiness_subscriptions_match_manager_topics_and_qos(self):
        self.monitor._setup_readiness_subscriptions(self.node)
        calls = self.node.create_subscription.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual({call.args[1] for call in calls}, {"/ur20/ready", "/nex10/ready"})
        for call in calls:
            msg_type, topic, callback, qos = call.args
            self.assertIs(msg_type, Bool)
            self.assertEqual(qos.depth, 1)
            self.assertEqual(qos.reliability, ReliabilityPolicy.RELIABLE)
            self.assertEqual(qos.durability, DurabilityPolicy.TRANSIENT_LOCAL)
            callback(Bool(data=False))
            self.assertIs(self.monitor._ready[topic.split('/')[1]], False)

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


class ReadinessSubscriptionTests(unittest.TestCase):
    def test_retained_false_and_live_recovery_over_ros(self):
        # Private test topics and mocked graph/tmux observations never operate
        # robot processes or publish to the cell's readiness topics.
        context = Context()
        rclpy.init(context=context)
        self.addCleanup(context.shutdown)
        node = Node('rgt_desk_readiness_test', context=context)
        self.addCleanup(node.destroy_node)
        executor = SingleThreadedExecutor(context=context)
        self.addCleanup(executor.shutdown)
        executor.add_node(node)
        monitor = ProcessMonitor()
        topic = f'/rgt_desk_test_{uuid.uuid4().hex}/ur20/ready'
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        publisher = node.create_publisher(Bool, topic, qos)
        publisher.publish(Bool(data=False))
        with patch.object(process_config, 'process_ready_topic',
                          side_effect=lambda name: topic if name == 'ur20' else None):
            monitor._setup_readiness_subscriptions(node)

        def wait_for(ready):
            deadline = time.monotonic() + 5
            while monitor._ready['ur20'] is not ready and time.monotonic() < deadline:
                executor.spin_once(timeout_sec=0.05)
            self.assertIs(monitor._ready['ur20'], ready)

        graph = Mock()
        graph.get_node_names_and_namespaces.return_value = [('ur_robot_manager', '/ur20')]
        with patch('process_monitor.tmux.get_windows', return_value=['ur20']):
            wait_for(False)
            monitor._update_status(graph)
            self.assertEqual(monitor.get_status()['ur20'], 'error')
            publisher.publish(Bool(data=True))
            wait_for(True)
            monitor._update_status(graph)
            self.assertEqual(monitor.get_status()['ur20'], 'running')


if __name__ == "__main__":
    unittest.main()
