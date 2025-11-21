import random
import cv2 as cv
import mss
import numpy as np
import os
import time
from input_handling import send_input
import concurrent.futures
import config as cfg

def take_screenshot(sct) -> np.ndarray:
    """Takes a screenshot of the second monitor."""
    monitor = sct.monitors[int(cfg.MONITOR_NUMBER)]
    screenshot = sct.grab(monitor)
    return cv.cvtColor(np.array(screenshot), cv.COLOR_BGRA2BGR)
def are_images_different(image1: np.ndarray, image2: np.ndarray, pixel_threshold: int = 30, percentage_threshold: float = 0.01) -> bool:
    """
    Compares two images to see if they are significantly different, ignoring minor changes.

    Args:
        image1: The first image.
        image2: The second image.
        pixel_threshold: The threshold for pixel value differences (0-255).
        percentage_threshold: The percentage of different pixels (0.0-1.0)
                              to consider the images different.

    Returns:
        bool: True if the images are significantly different, False otherwise.
    """
    if image1.shape != image2.shape:
        return True

    # Calculate the absolute difference between the two images
    diff = cv.absdiff(image1, image2)
    gray_diff = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)

    # Create a binary image of the differences
    _, thresh_diff = cv.threshold(gray_diff, pixel_threshold, 255, cv.THRESH_BINARY)

    # Count the number of different pixels
    diff_pixels = np.count_nonzero(thresh_diff)
    total_pixels = image1.shape[0] * image1.shape[1]

    # Calculate the percentage of different pixels
    diff_percentage = diff_pixels / total_pixels

    return diff_percentage > percentage_threshold
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
        template = templates[template_name]
        result = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(result)
        return template_name, max_val >= tolerance

    detection_dict = {}
    # Use a thread pool to run template matching concurrently, limiting workers
    # to match VM vCPUs for efficiency.
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg.MULTITHREADING_MAX_WORKERS) as executor: # Set max_workers here
        results = executor.map(evaluate_template, templates.keys())
        for template_name, is_detected in results:
            detection_dict[template_name] = is_detected
    return detection_dict
def next_iteration(sct):
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



print("Starting bot in 5 seconds...")
time.sleep(5)
template_names = os.listdir(cfg.TEMPLATES_FOLDER_PATH)
templates = {}
for template_name in template_names:
    templates[template_name] = cv.imread(os.path.join(cfg.TEMPLATES_FOLDER_PATH, template_name))
try:
    with mss.mss() as sct:
        i = 0
        while True:
            print(f"Starting iteration number: {i}")
            next_iteration(sct)
            i += 1
            time.sleep(random.uniform(0.4, 0.8))
except KeyboardInterrupt:
    print("\nBot stopped by user.")