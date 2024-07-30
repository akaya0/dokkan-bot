import cv2
import numpy as np
import time
from adbutils import adb
import adbutils
import os
import io
import json
import os
import math
import sys
import argparse

device = adbutils.AdbClient(host="127.0.0.1", port=5037).device() 
baseY = 1520   
baseX = 720

result = device.shell("wm size")
if 'size' in result:
    resolution = result.split(":")[-1].strip()
    width, height = resolution.split('x')
            
    width_ratio =  int(width) / baseX 
    height_ratio = int(height) / baseY         
                    
    diagonal1 = math.sqrt(int(width)**2 + int(height)**2)
    diagonal2 = math.sqrt(baseX**2 + baseY**2)
    overall_scale_ratio = diagonal1 / diagonal2
            
    print(f"Screen Scale Ratio: {overall_scale_ratio}\n")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Dokkan automation script. Farms Dokkan indefinetly on an Android device via ADB and OpenCV.'
    )
    parser.add_argument(
        '-d', '--difficulty', 
        type=int, 
        choices=range(0, 6),
        default=0, 
        help='Select difficulty level (0: EZA, 1: Hard, 2: Z-Hard, 3: Super, 4: Super2, 5: Super3).'
    )
    parser.add_argument(
        '-c', '--config', 
        type=str, 
        default='actions_config.json', 
        help='Path to the configuration file (JSON).'
    )

    return parser.parse_args()

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
    if img.dtype != template.dtype:
        img = img.astype(np.float32) if template.dtype == np.float32 else img.astype(np.uint8)
        template = template.astype(np.float32) if img.dtype == np.float32 else template.astype(np.uint8)
    return img, template


def resize_image(image):
    global width_ratio, height_ratio
    original_height, original_width = image.shape[:2]
    # Calculate the new dimensions
    new_width = int(original_width * width_ratio)
    new_height = int(original_height * height_ratio)
    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    return resized_image

def clear_last_line():
    # Move the cursor up one line
    sys.stdout.write('\033[A')
    # Clear the line
    sys.stdout.write('\033[K')
    # Flush the output to ensure it is displayed immediately
    sys.stdout.flush()

def find_template(screenshot, template, threshold=0.8):
    #Convert images to grayscale
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) if len(screenshot.shape) == 3 else screenshot
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
    
    # Resize screenshot
    template_gray = resize_image(template_gray)
    
    # Perform template matching
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Return the location if the match value exceeds the threshold
    return max_loc if max_val > threshold else None
    
def tap(x, y):
    device.shell(f"input tap {x} {y}")
    
    
def perform_action(screenshot, template, action_name, last_performed, timeout=2):
    current_time = time.time()
    
    if action_name in last_performed and current_time - last_performed[action_name] < timeout:
        return False

    location = find_template(screenshot, template)
    if location:
        tap(location[0] + template.shape[1] // 2, location[1] + template.shape[0] // 2)
        clear_last_line() 
        print(f"last action performed: {action_name}")
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

def handle_difficulty(difficulty, screenshot, actions, last_performed):
    levels = {
        1: [('hard_level', 'hard_level_s')],
        2: [('z-hard_level', 'z-hard_level_s')],
        3: [('super_level', 'super_level_s')],
        4: [('super2_level',)],
        5: [('super3_level',)]
    }
    
    if difficulty == 0:
        return
    
    # Retrieve levels based on difficulty
    for level_pair in levels.get(difficulty, []):
        for level in level_pair:
            if perform_action(screenshot, actions[level], level, last_performed):
                return # or continue, based on your loop structure

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
    args = parse_arguments()
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, args.config)
    
    actions = load_actions_from_config(config_path)
    last_performed = {}
    
    difficulty = args.difficulty

    while True:

        image_bytes = take_screenshot()
        screenshot = load_image(image_bytes)
        
        handle_difficulty(difficulty, screenshot, actions, last_performed)
   
        if perform_action(screenshot, actions['attempt_again'], 'attempt_again', last_performed):
            continue
        
        for action_name, template in actions.items():
            if action_name not in ['attempt_again']:
                if perform_action(screenshot, template, action_name, last_performed):
                    break

if __name__ == "__main__":
    main()