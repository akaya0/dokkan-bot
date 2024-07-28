import cv2
import numpy as np
import time
from adbutils import adb
import os
import io
import json
import os

scale = 1.0
device = adb.device()

def scaling():
    global scale
    
    result = device.shell("wm size")
    print(f"{result}") 

def take_screenshot():
    try:
        # Execute the screencap command and capture the output
        result = device.shell("screencap -p", stream=True)
        
        if result is None:
            raise RuntimeError("Failed to execute screencap command.")
        
        # Read the screenshot data in chunks
        image_bytes = bytearray()
        chunk_size = 4096  # Adjust chunk size if needed
        while True:
            chunk = result.read(chunk_size)
            if not chunk:
                break
            image_bytes.extend(chunk)

        # Wrap in BytesIO
        image_stream = io.BytesIO(image_bytes)

        return image_stream

    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

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

def tap(x, y):
    print(f"Attempting to tap at coordinates: ({x}, {y})")
    result = device.shell(f"input tap {x} {y}")
    print(f"Tap result: {result}")

def find_template(screenshot, template, threshold=0.8,):
    global scale
    
    screenshot_gray = cv2.resize(template, (0, 0), fx=scale, fy=scale)
    # Convert images to grayscale
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template

    # Normalize images
    screenshot_gray = cv2.normalize(screenshot_gray, None, 0, 255, cv2.NORM_MINMAX)
    template_gray = cv2.normalize(template_gray, None, 0, 255, cv2.NORM_MINMAX)
    
    
    
    
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # Return the location if the match value exceeds the threshold
    return max_loc if max_val > threshold else None

def perform_action(screenshot, template, action_name, last_performed, timeout=10):
    global scale
    
    current_time = time.time()
    if action_name in last_performed and current_time - last_performed[action_name] < timeout:
        print(f"Action '{action_name}' was performed recently. Skipping.")
        return False

    location = find_template(screenshot, template)
    if location:
        # Adjust tap coordinates based on the scale
        tap_x = int(location[0] + (template.shape[1] / 2) * scale)
        tap_y = int(location[1] + (template.shape[0] / 2) * scale)
        print(f"Found template at location: ({location[0]}, {location[1]}) with scale: {scale}")
        print(f"Calculated tap coordinates: ({tap_x}, {tap_y})")
        tap(tap_x, tap_y)
        cls()
        print(f"Last action performed: {action_name}")
        last_performed[action_name] = current_time
        return True
    print(f"Template not found for action: {action_name}")

def load_actions_from_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    actions = {}
    for action_name, template_path in config['actions'].items():
        actions[action_name] = load_image(open(template_path, 'rb'))
    return actions

def get_input(prompt, min_value, max_value):
    while True:
        try:
            value = int(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter an integer between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
                      
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'actions_config.json')
    
    actions = load_actions_from_config(config_path)
    last_performed = {}
    
    
    difficulty = get_input("Difficulty [(0)EZA (1)hard (2)z-hard (3)super (4)super2 (5)super3]: ", 0, 5)
 
    cls()
    
    while True:
        image_bytes = take_screenshot()
        screenshot = load_image(image_bytes)
        
        match difficulty:
            case 0: 
                continue
            case 1:
                if perform_action(screenshot, actions['hard_level'], 'hard_level', last_performed):
                    continue
                elif perform_action(screenshot, actions['hard_level_s'], 'hard_level_s', last_performed):
                    continue       
            case 2:
                if perform_action(screenshot, actions['z-hard_level'], 'z-hard_level', last_performed):
                    continue
                elif perform_action(screenshot, actions['z-hard_level_s'], 'z-hard_level_s', last_performed):
                    continue       
            case 3:
                if perform_action(screenshot, actions['super_level'], 'super_level', last_performed):
                    continue
                elif perform_action(screenshot, actions['super_level_s'], 'super_level_s', last_performed):
                    continue       
            case 4:
                if perform_action(screenshot, actions['super2_level'], 'super2_level', last_performed):
                    continue 
            case 5:
                if perform_action(screenshot, actions['super3_level'], 'super3_level', last_performed):
                    continue
             
        if perform_action(screenshot, actions['friend_request'], 'friend_request', last_performed):
            continue        
        if perform_action(screenshot, actions['friend_acc'], 'friend_acc', last_performed):
            continue
        if perform_action(screenshot, actions['attempt_again'], 'attempt_again', last_performed):
            continue
        
        for action_name, template in actions.items():
            if action_name not in ['friend_acc', 'friend_request', 'hard_level', 'z-hard_level', 'super_level', 'super2_level', 'super3_level' 'hard_level_s', 'z-hard_level_s', 'super_level_s','attempt_again']:
                if perform_action(screenshot, template, action_name, last_performed):
                    break

if __name__ == "__main__":
    main()