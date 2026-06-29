"""
=========================================================
Touchless Hand Tracking Suite
Version : V4.0 (Optimized Architecture)
Author  : Production Refactored Edition
=========================================================
"""

import os

# =====================================================
# CAMERA SETTINGS
# =====================================================
CAM_WIDTH = 1280
CAM_HEIGHT = 720
CAMERA_ID = 1
FPS_TARGET = 30

# =====================================================
# MEDIAPIPE SETTINGS
# =====================================================
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7
MODEL_COMPLEXITY = 0  # 0 for speed, 1 for balanced precision

# =====================================================
# UI CONTROLLER SETTINGS
# =====================================================
SMOOTHING = 3  # Reduced for faster operational response
MOUSE_FRAME_REDUCTION = 120
CLICK_THRESHOLD = 35
CLICK_COOLDOWN = 0.35

# =====================================================
# DRAWING SETTINGS
# =====================================================
DEFAULT_BRUSH_SIZE = 5
MIN_BRUSH_SIZE = 2
MAX_BRUSH_SIZE = 40
ERASER_SIZE = 60

# =====================================================
# COLOR PALETTE (BGR)
# =====================================================
COLORS = {
    "Blue": (255, 0, 0),
    "Green": (0, 255, 0),
    "Red": (0, 0, 255),
    "Yellow": (0, 255, 255),
    "Purple": (255, 0, 255),
    "White": (255, 255, 255),
    "Black": (0, 0, 0)
}
DEFAULT_COLOR = COLORS["Blue"]

# =====================================================
# GESTURE DEFINITIONS
# =====================================================
GESTURES = {
    "DRAW": [0, 1, 0, 0, 0],
    "SELECT": [0, 1, 1, 0, 0],
    "ERASE": [0, 1, 1, 1, 0],
    "CLEAR": [1, 1, 1, 1, 1],
    "AI_TRIGGER": [0, 0, 0, 0, 0]
}

# =====================================================
# EASYOCR SETTINGS
# =====================================================
OCR_LANGUAGES = ['en']
OCR_GPU = False  # Set to True if local CUDA runtime environment is available

# =====================================================
# SHAPE DETECTION SETTINGS
# =====================================================
MIN_SHAPE_AREA = 800
CONTOUR_APPROX_FACTOR = 0.035

# =====================================================
# RECORDING SETTINGS
# =====================================================
RECORDING_FOLDER = "recordings"
if not os.path.exists(RECORDING_FOLDER):
    os.makedirs(RECORDING_FOLDER)

VIDEO_CODEC = "XVID"
VIDEO_FPS = 25

# =====================================================
# SCREENSHOT SETTINGS
# =====================================================
SCREENSHOT_FOLDER = "screenshots"
if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)

# =====================================================
# UI RENDERING STYLES
# =====================================================
TEXT_COLOR = (255, 255, 255)
SUCCESS_COLOR = (0, 255, 0)
WARNING_COLOR = (0, 255, 255)
ERROR_COLOR = (0, 0, 255)
HEADER_HEIGHT = 100

COLOR_BUTTONS = {
    "Blue": (50, 250),
    "Green": (300, 500),
    "Red": (550, 750),
    "Yellow": (800, 1000),
    "Eraser": (1050, 1250)
}

# =====================================================
# SYSTEMIC OPTIMIZATION FEATURES
# =====================================================
ENABLE_FPS_DISPLAY = True
ENABLE_RECORDING = True
ENABLE_OCR = True
ENABLE_SHAPE_RECOGNITION = True
AI_TRIGGER_COOLDOWN = 1.5
ENABLE_DYNAMIC_BRUSH = True
PINCH_MIN_DISTANCE = 25
PINCH_MAX_DISTANCE = 160
WINDOW_NAME = "Touchless Hand Tracking Suite V4"