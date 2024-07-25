import cv2
import numpy as np
import time
from adbutils import adb
import os
import io
import json

# Connect to the device
device = adb.device()

def take_screenshot():
    # Capture the screenshot and return it as a byte stream
    image_bytes = device.shell("screencap -p", stream=True).read(9999999)  # Read a large number of bytes
    image_bytes = io.BytesIO(image_bytes)
    return image_bytes

def load_image(image_bytes):
    # Load the image from the byte stream
    img = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Image could not be loaded.")
    return img

def ensure_same_type_and_depth(img, template):
    if img.dtype != template.dtype or img.shape[2] != template.shape[2]:
        img = img.astype(np.float32) if template.dtype == np.float32 else img.astype(np.uint8)
        template = template.astype(np.float32) if img.dtype == np.float32 else template.astype(np.uint8)
    return img, template

def find_template(screenshot, template):
    screenshot, template = ensure_same_type_and_depth(screenshot, template)
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_loc if max_val > 0.8 else None  # Adjust the threshold as needed

def tap(x, y):
    device.shell(f"input tap {x} {y}")

def perform_action(screenshot, template, action_name, last_performed, timeout=10):
    current_time = time.time()
    if action_name in last_performed and current_time - last_performed[action_name] < timeout:
        return False
    
    location = find_template(screenshot, template)
    if location:
        tap(location[0] + template.shape[1] // 2, location[1] + template.shape[0] // 2)
        print(f"{action_name} action performed")
        last_performed[action_name] = current_time
        return True
    return False

def load_actions_from_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    actions = {}
    for action_name, template_path in config['actions'].items():
        actions[action_name] = load_image(open(template_path, 'rb'))
    return actions

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'actions_config.json')
    
    actions = load_actions_from_config(config_path)
    last_performed = {}

    while True:
        image_bytes = take_screenshot()
        screenshot = load_image(image_bytes)
        
        if perform_action(screenshot, actions['friend_acc'], 'friend_acc', last_performed):
            time.sleep(1)
            continue
        
        if perform_action(screenshot, actions['friend_request'], 'friend_request', last_performed):
            time.sleep(1)
            continue
        
        for action_name, template in actions.items():
            if action_name not in ['friend_acc', 'friend_request']:
                if perform_action(screenshot, template, action_name, last_performed):
                    time.sleep(1)
                    break

if __name__ == "__main__":
    main()