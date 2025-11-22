import json
import os
import cv2 as cv

filename = os.path.join("ZuBotPrivateConfig", "VM", "Config.JSON")
with open(filename) as f:
    config = json.load(f)
WINDOW_TITLE = config["WINDOW_TITLE"]
PROCESS_NAME = config["PROCESS_NAME"]
STEAM_URL = config["STEAM_URL"]
MONITOR_NUMBER : int = config["MONITOR_NUMBER"]
MULTITHREADING_MAX_WORKERS : int = config["MULTITHREADING_MAX_WORKERS"]

template_names = os.listdir(config["TEMPLATES_FOLDER_PATH"])
TEMPLATES = {}
for template_name in template_names:
    TEMPLATES[template_name] = cv.imread(os.path.join(config["TEMPLATES_FOLDER_PATH"], template_name))
