import libtmux
import time

TMUX_SESSION_NAME = "rgt"
tmux_server = libtmux.Server()

def get_main_session() -> libtmux.Session:
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
