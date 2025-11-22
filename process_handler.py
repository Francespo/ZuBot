import config as cfg
import time
import subprocess

def is_game_running() -> bool:
    check = subprocess.run(f"tasklist /FI \"IMAGENAME eq {cfg.PROCESS_NAME}.exe\"", shell=True, capture_output=True, text=True)
    return cfg.PROCESS_NAME.lower() in check.stdout.lower()
def quit_game() -> None:
    attempt = 0
    while is_game_running():
        _safe_quit()
        attempt += 1
        if attempt > 5:
            _force_quit()
    time.sleep(8)

def _safe_quit() -> None:
    gentle_close_command = f"""
        $p = Get-Process -Name "{cfg.PROCESS_NAME}" -ErrorAction SilentlyContinue
        if ($p) {{
            $p.CloseMainWindow() | Out-Null
            $p.WaitForExit(10000)
        }}
        """
    subprocess.run(["powershell", "-Command", gentle_close_command], shell=True)
def _force_quit() -> None:
    subprocess.run(f"taskkill /F /IM {cfg.PROCESS_NAME}.exe", shell=True)
def start_game() -> None:
    subprocess.run(f"start {cfg.STEAM_URL}", shell=True)