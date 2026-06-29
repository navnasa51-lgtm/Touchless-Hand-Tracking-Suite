"""
=========================================================
CANVAS DRAWING MODULE
Touchless Hand Tracking Suite V5.0
=========================================================
"""

import cv2
import numpy as np
import config

class CanvasModule:
    def __init__(self):
        # Isolated canvas tracking matrix
        self.canvas = np.zeros((config.CAM_HEIGHT, config.CAM_WIDTH, 3), dtype=np.uint8)
        self.draw_color = config.DEFAULT_COLOR
        self.brush_size = config.DEFAULT_BRUSH_SIZE
        self.xp, self.yp = 0, 0

    def reset_tracking(self):
        """Flushes structural tracking points to prevent trailing lines across frames."""
        self.xp, self.yp = 0, 0

    def clear_canvas(self):
        self.canvas[:] = 0
        self.reset_tracking()

    def draw_palette(self, frame):
        cv2.rectangle(frame, (50, 10), (250, 90), config.COLORS["Blue"], cv2.FILLED)
        cv2.rectangle(frame, (300, 10), (500, 90), config.COLORS["Green"], cv2.FILLED)
        cv2.rectangle(frame, (550, 10), (750, 90), config.COLORS["Red"], cv2.FILLED)
        cv2.rectangle(frame, (800, 10), (1000, 90), config.COLORS["Yellow"], cv2.FILLED)
        cv2.rectangle(frame, (1050, 10), (1250, 90), (255, 255, 255), cv2.FILLED)
        cv2.putText(frame, "ERASER", (1080, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    def merge_layers(self, frame):
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, inv)
        frame = cv2.bitwise_or(frame, self.canvas)
        return frame

    def process_interaction(self, frame, lm_list, fingers, index_pos):
        if not index_pos:
            self.reset_tracking()
            return frame

        x1, y1 = index_pos
        thumb, index, middle, ring, pinky = fingers[0], fingers[1], fingers[2], fingers[3], fingers[4]

        # Dynamic brush size calibration via micro-pinches
        if config.ENABLE_DYNAMIC_BRUSH and len(lm_list) > 0:
            # Distance calculated dynamically from tracker parameters
            x_mid, y_mid = lm_list[12][1], lm_list[12][2]
            distance = np.hypot(lm_list[4][1] - x_mid, lm_list[4][2] - y_mid)
            distance = max(config.PINCH_MIN_DISTANCE, min(distance, config.PINCH_MAX_DISTANCE))
            norm = (distance - config.PINCH_MIN_DISTANCE) / (config.PINCH_MAX_DISTANCE - config.PINCH_MIN_DISTANCE)
            self.brush_size = int(norm * (config.MAX_BRUSH_SIZE - config.MIN_BRUSH_SIZE) + config.MIN_BRUSH_SIZE)

        # GESTURE: SELECTION / TOOL NAVIGATION (Index + Middle Extended Up)
        if index == 1 and middle == 1 and ring == 0 and pinky == 0:
            self.reset_tracking()
            if y1 < config.HEADER_HEIGHT:
                if 50 < x1 < 250:
                    self.draw_color = config.COLORS["Blue"]
                elif 300 < x1 < 500:
                    self.draw_color = config.COLORS["Green"]
                elif 550 < x1 < 750:
                    self.draw_color = config.COLORS["Red"]
                elif 800 < x1 < 1000:
                    self.draw_color = config.COLORS["Yellow"]
                elif 1050 < x1 < 1250:
                    self.draw_color = (0, 0, 0) # Eraser Selection State

        # GESTURE: ACTIVE WRITING MODE (Index up, Middle closed)
        elif index == 1 and middle == 0 and ring == 0 and pinky == 0:
            if self.xp == 0 and self.yp == 0:
                self.xp, self.yp = x1, y1

            if self.draw_color == (0, 0, 0): # Eraser context mode
                cv2.line(self.canvas, (self.xp, self.yp), (x1, y1), (0, 0, 0), config.ERASER_SIZE)
            else:
                cv2.circle(frame, (x1, y1), self.brush_size, self.draw_color, cv2.FILLED)
                cv2.line(self.canvas, (self.xp, self.yp), (x1, y1), self.draw_color, self.brush_size)
            self.xp, self.yp = x1, y1

        # GESTURE: CHORD ERASER MODE (Index + Middle + Ring Extended Up)
        elif index == 1 and middle == 1 and ring == 1 and pinky == 0:
            if self.xp == 0 and self.yp == 0:
                self.xp, self.yp = x1, y1
            cv2.line(self.canvas, (self.xp, self.yp), (x1, y1), (0, 0, 0), config.ERASER_SIZE)
            self.xp, self.yp = x1, y1
        else:
            self.reset_tracking()

        self.draw_palette(frame)
        return self.merge_layers(frame)