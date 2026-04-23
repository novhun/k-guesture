import json
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "assets/fonts/Battambang.ttf"
JSON_OUTPUT = "current_gesture.json"

def get_khmer_font(size=32):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except IOError:
        # Fallback to default if font not found
        return ImageFont.load_default()

def draw_khmer_text(cv_image, text, position=(50, 50), font_size=40, color=(0, 255, 0)):
    """
    OpenCV doesn't natively support rendering complex unicode like Khmer.
    We convert to PIL, draw the text, and convert back to OpenCV format.
    """
    # Convert OpenCV image (BGR) to PIL image (RGB)
    cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv_image_rgb)
    
    draw = ImageDraw.Draw(pil_image)
    font = get_khmer_font(size=font_size)
    
    # Draw text
    draw.text(position, text, font=font, fill=color)
    
    # Convert back to OpenCV BGR
    cv_image_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return cv_image_bgr

def write_current_gesture(english_label, khmer_label):
    """
    Writes the currently detected gesture to a JSON file for the Web project to read.
    """
    data = {
        "english": english_label,
        "khmer": khmer_label
    }
    
    # Write to a temporary file then rename to avoid race conditions when web project reads
    temp_file = JSON_OUTPUT + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    os.replace(temp_file, JSON_OUTPUT)

def clear_current_gesture():
    """
    Clears the current gesture json when no gesture is detected.
    """
    write_current_gesture("", "")
