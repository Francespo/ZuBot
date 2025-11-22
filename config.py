import json
import os

filename = os.path.join("ZuBotPrivateConfig", "VM", "Config.JSON")
with open(filename) as f:
    config = json.load(f)
WINDOW_TITLE = config["WINDOW_TITLE"]
PROCESS_NAME = config["PROCESS_NAME"]
STEAM_URL = config["STEAM_URL"]
MONITOR_NUMBER : int = config["MONITOR_NUMBER"]
TEMPLATES_FOLDER_PATH = config["TEMPLATES_FOLDER_PATH"]
MULTITHREADING_MAX_WORKERS : int = config["MULTITHREADING_MAX_WORKERS"]