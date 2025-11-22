from input_handler import send_input
import config as cfg
import process_handler as game_process
import random
import cv2 as cv
import mss
import numpy as np
import time
import concurrent.futures

class StuckCounters:
    loading_screen_iterations = 0
    def __init__(self):
        self.loading_screen_iterations = 0


def take_screenshot(sct) -> np.ndarray:
    """Takes a screenshot of the second monitor."""
    monitor = sct.monitors[int(cfg.MONITOR_NUMBER)]
    screenshot = sct.grab(monitor)
    return cv.cvtColor(np.array(screenshot), cv.COLOR_BGRA2BGR)
def generate_detection_dict(image: np.ndarray, tolerance: float) -> dict[str, bool]:
    """
    Args:
        image: The image to search in.
        tolerance: The matching tolerance for template matching.

    Returns:
        A dictionary where keys are template names and values are booleans
        indicating if the template was found.
    """
    def evaluate_template(template_name: str) -> tuple[str, bool]:
        """Evaluates a single template and returns its name and whether it was found."""
        template = cfg.TEMPLATES[template_name]
        result = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(result)
        return template_name, max_val >= tolerance

    detection_dict = {}
    # Use a thread pool to run template matching concurrently, limiting workers
    # to match VM vCPUs for efficiency.
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg.MULTITHREADING_MAX_WORKERS) as executor: # Set max_workers here
        results = executor.map(evaluate_template, cfg.TEMPLATES.keys())
        for template_name, is_detected in results:
            detection_dict[template_name] = is_detected
    return detection_dict
def next_iteration(sct, stuck : StuckCounters):
    """Takes a screenshot and performs the next action based on screen content."""
    img = take_screenshot(sct)
    detection = generate_detection_dict(img, 0.90)
    del img

    if detection["bb_home_transmitting.png"] or detection["bb_lobbys_searchingforopponent.png"]:
        print("waiting for connection to end")
    elif detection["bb_home.png"]:
        if detection["bb_home_ multiplayer_button.png"]:
            print("I am in the bb home, the multiplayer button is highlighted")
            send_input("enter")
            time.sleep(random.uniform(5, 6))
        else:
            print("I am in the bb home, the multiplayer button is not highlighted")
            send_input("down")
    elif detection["bb_lobbys_search_button.png"]:
        print("I am in the bb lobby screen, the search panel is being shown")
        send_input("e")
    elif detection["bb_lobbys.png"]:
        if detection["bb_lobbys_quickmatch_button.png"]:
            print("I am in the bb home, the quick search button is highlighted")
            send_input("enter")
            time.sleep(random.uniform(3, 4))
        else:
            print("I am in the bb home, the quick search button is not highlighted")
            send_input("down")
    elif detection["bb_teamselect.png"]:
        print("I am in the team selection screen")
        send_input("enter")
    elif detection["match_next_button.png"]:
        print("I am in-game")
        send_input("enter")
        time.sleep(random.uniform(4, 5))
    elif detection["match_formationset_button.png"]:
        print("I am in-game, waiting for formations to be set")
        send_input("alt")
    elif detection["banner_interaction_mark.png"]:
        print("I am facing a banner")
        send_input("enter")
    elif detection["loading.png"]:
        print("I am in the blue loading screen")
        stuck.loading_screen_iterations += 1
        if stuck.loading_screen_iterations >= 10:
            print("I got stuck loading")
            restart_and_go_to_main_menu()
            go_to_bb_from_main_menu()
            print("I should be ready to play now")
            stuck.loading_screen_iterations = 0
        time.sleep(random.uniform(5, 6))
        return
    else:
        print("I don't know where I am")
    stuck.loading_screen_iterations = 0
def restart_and_go_to_main_menu():
    print("I'm restarting the game")
    game_process.quit_game()
    game_process.start_game()
    time.sleep(random.uniform(65, 70))
    send_input("enter")
    time.sleep(random.uniform(5, 6))
    send_input("enter")
    time.sleep(random.uniform(6, 8))
    send_input("enter")
    time.sleep(random.uniform(8, 10))
def go_to_bb_from_main_menu():
    print("I'm going in the bb")
    for i in range(4):
        send_input("right")
        time.sleep(random.uniform(1, 2))
    send_input("enter")

print("Starting bot in 5 seconds...")
time.sleep(5)
stuck = StuckCounters()
if not game_process.is_game_running():
    print("The game is not open")
    restart_and_go_to_main_menu()
    go_to_bb_from_main_menu()
    print("I should be ready to play now")
else:
    print("The game is already open")
try:
    with mss.mss() as sct:
        i = 0
        while True:
            print(f"{i} - ", end="")
            next_iteration(sct, stuck)
            i += 1
            time.sleep(random.uniform(0.4, 0.8))
except KeyboardInterrupt:
    print("\nBot stopped by user.")