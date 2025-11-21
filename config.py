import json
import os

filename = os.path.join("ZuBotPrivateConfig", "VM", "Config.JSON")
with open(filename) as f:
    config = json.load(f)
WINDOW_TITLE = config["WINDOW_TITLE"]
MONITOR_NUMBER = config["MONITOR_NUMBER"]
TEMPLATES_FOLDER_PATH = config["TEMPLATES_FOLDER_PATH"]
MULTITHREADING_MAX_WORKERS = config["MULTITHREADING_MAX_WORKERS"]