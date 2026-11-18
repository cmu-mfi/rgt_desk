import libtmux
import os
import shlex
import threading
import time

TMUX_SESSION_NAME = "rgt"
tmux_server = libtmux.Server()
_session_lock = threading.Lock()

def get_main_session() -> libtmux.Session:
    with _session_lock:
        session = tmux_server.sessions.get(session_name=TMUX_SESSION_NAME, default=None)
        if not session:
            session = tmux_server.new_session(session_name=TMUX_SESSION_NAME, window_name="main")
        return session

def get_windows() -> list[str]:
    session = get_main_session()
    windows = []
    for window in session.windows:
        if window.window_name == "main":
            continue
        windows.append(window.window_name)
    return windows

def start_process(name: str, command: str):
    session = get_main_session()
    if session.windows.get(window_name=name, default=None):
        return 
    window = session.new_window(window_name=name, attach=False)
    pane = window.active_pane
    if pane:
        pane.send_keys(command, enter=True)

def stop_process(name: str):
    session = get_main_session()
    window = session.windows.get(window_name=name, default=None)
    if window:
        pane = window.active_pane
        pane.send_keys('C-c')
        time.sleep(1)
        window.kill()

def get_logs(name: str, lines: int = 100) -> list[str]:
    """Last `lines` lines of a process window's terminal (pane history).

    Returns an empty list when the window does not exist (process stopped).
    Output is plain text as rendered by tmux (`capture-pane -p -S -{lines}`):
    ANSI colors stripped, long lines wrapped to the pane width.
    """
    lines = max(1, int(lines))
    session = get_main_session()
    window = session.windows.get(window_name=name, default=None)
    if not window:
        return []
    try:
        pane = window.active_pane
        if not pane:
            return []
        result = pane.capture_pane(start=f"-{lines}")
    except libtmux.exc.LibTmuxException:
        if not session.windows.get(window_name=name, default=None):
            return []  # The command exited during the terminal capture.
        raise
    out = getattr(result, "stdout", result)
    if isinstance(out, str):
        return out.splitlines()
    return [line.rstrip() for line in out if line is not None]


def service_window_name(name: str) -> str:
    # Keep service windows separate from process windows, even for equal IDs.
    return f"service-{name}"


def start_service(name: str, command: str):
    session = get_main_session()
    window_name = service_window_name(name)
    previous = session.windows.get(window_name=window_name, default=None)
    if previous:
        previous.kill()
    # Close the window on exit, overriding any inherited retention setting.
    wrapper = (
        'tmux set-option -p -t "$TMUX_PANE" remain-on-exit off && '
        f'exec /bin/sh -c {shlex.quote(command)}'
    )
    try:
        session.new_window(
            window_name=window_name,
            window_shell=f"exec /bin/sh -c {shlex.quote(wrapper)}",
            start_directory=os.getcwd(),
            # An existing tmux server may predate ROS/workspace setup. Use the
            # same environment as the former subprocess-based service calls.
            environment={key: value for key, value in os.environ.items()
                         if key not in ("TMUX", "TMUX_PANE")},
            attach=False,
        )
    except libtmux.exc.TmuxObjectDoesNotExist:
        # new_window succeeded, but the command exited before libtmux could
        # refresh its Window object. There is nothing left to track.
        pass


def get_service_status(name: str):
    """Read state from tmux itself, including across backend restarts."""
    window = get_main_session().windows.get(
        window_name=service_window_name(name), default=None
    )
    try:
        pane = window.active_pane if window else None
    except libtmux.exc.LibTmuxException:
        if not get_main_session().windows.get(window_name=service_window_name(name), default=None):
            return "idle"
        raise
    return "executing" if pane and pane.pane_dead != "1" else "idle"


def cancel_service(name: str):
    """Interrupt the client and remove its window if it does not exit."""
    session = get_main_session()
    window_name = service_window_name(name)
    window = session.windows.get(window_name=window_name, default=None)
    if not window:
        return
    pane = window.active_pane
    if pane:
        pane.send_keys("C-c", enter=False)
        for _ in range(10):
            time.sleep(0.1)
            window = session.windows.get(window_name=window_name, default=None)
            if not window:
                return
            pane = window.active_pane
            if not pane or pane.pane_dead == "1":
                break
    window.kill()
