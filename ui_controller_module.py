"""
=========================================================
GUI OS INTERACTION CONTROLLER
Touchless Hand Tracking Suite V5.0
=========================================================
"""

import time
import numpy as np
import pyautogui
import config


class UiControllerModule:
    def __init__(self):
        # Absolute system execution overrides
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True

        self.screen_w, self.screen_h = pyautogui.size()
        self.ploc_x, self.ploc_y = 0, 0
        self.last_click_time = 0

    def reset_tracking(self):
        """Flushes historical position coordinates to eliminate position jumping on entry."""
        self.ploc_x, self.ploc_y = 0, 0

    def process_interaction(self, tracker, lm_list, fingers, index_pos):
        if not index_pos:
            self.reset_tracking()
            return

        x1, y1 = index_pos
        thumb, index, middle, ring, pinky = fingers[0], fingers[1], fingers[2], fingers[3], fingers[4]

        # TRACKING GESTURE: Pure Pointing (Index Up, Middle down)
        if index == 1 and middle == 0 and ring == 0 and pinky == 0:
            # Interpolate raw capture metrics across screen resolution matrices
            x3 = np.interp(x1, (config.MOUSE_FRAME_REDUCTION, config.CAM_WIDTH - config.MOUSE_FRAME_REDUCTION),
                           (0, self.screen_w))
            y3 = np.interp(y1, (config.MOUSE_FRAME_REDUCTION, config.CAM_HEIGHT - config.MOUSE_FRAME_REDUCTION),
                           (0, self.screen_h))

            # Apply Exponential Moving Average (EMA) smoothing vectors
            if self.ploc_x == 0 and self.ploc_y == 0:
                cloc_x, cloc_y = x3, y3
            else:
                cloc_x = self.ploc_x + (x3 - self.ploc_x) / config.SMOOTHING
                cloc_y = self.ploc_y + (y3 - self.ploc_y) / config.SMOOTHING

            # Map position directly to system desktop workspace
            pyautogui.moveTo(cloc_x, cloc_y)
            self.ploc_x, self.ploc_y = cloc_x, cloc_y

            # Check for micro-pinch click gestures while moving the cursor
            pinch_dist = tracker.pinch_distance(lm_list)
            if pinch_dist < config.CLICK_THRESHOLD:
                now = time.time()
                if now - self.last_click_time > config.CLICK_COOLDOWN:
                    pyautogui.click()
                    self.last_click_time = now
        else:
            self.reset_tracking()