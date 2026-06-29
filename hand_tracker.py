"""
=========================================================
Hand Tracker Module (Optimized)
Touchless Hand Tracking Suite V4+
=========================================================
"""

import cv2
import mediapipe as mp
import math
import config

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            model_complexity=config.MODEL_COMPLEXITY,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None
        self.current_handedness = "Right"

    def find_hands(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

        if self.results.multi_hand_landmarks:
            # Extract dominant handedness classification label
            if self.results.multi_handedness:
                self.current_handedness = self.results.multi_handedness[0].classification[0].label

            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
        return frame

    def get_landmarks(self, frame):
        lm_list = []
        if not self.results or not self.results.multi_hand_landmarks:
            return lm_list

        hand = self.results.multi_hand_landmarks[0]
        h, w, _ = frame.shape
        for idx, lm in enumerate(hand.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append([idx, cx, cy])
        return lm_list

    def fingers_up(self, lm_list):
        fingers = []
        if len(lm_list) == 0:
            return fingers

        # Context-Aware Thumb Evaluation (Dynamically calibrated for Left/Right structures)
        # Uses horizontal orientation normalized against base infrastructure joints
        if self.current_handedness == "Right":
            if lm_list[self.tip_ids[0]][1] > lm_list[self.tip_ids[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if lm_list[self.tip_ids[0]][1] < lm_list[self.tip_ids[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Standard Core Phalanges Evaluation Loop
        for i in range(1, 5):
            if lm_list[self.tip_ids[i]][2] < lm_list[self.tip_ids[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def get_distance(self, p1, p2, lm_list):
        if len(lm_list) == 0: return 0
        return math.hypot(lm_list[p2][1] - lm_list[p1][1], lm_list[p2][2] - lm_list[p1][2])

    def pinch_distance(self, lm_list):
        return self.get_distance(4, 8, lm_list)

    def brush_size_from_pinch(self, lm_list):
        if len(lm_list) == 0:
            return config.DEFAULT_BRUSH_SIZE

        distance = self.get_distance(4, 12, lm_list)
        distance = max(config.PINCH_MIN_DISTANCE, min(distance, config.PINCH_MAX_DISTANCE))

        normalized_span = (distance - config.PINCH_MIN_DISTANCE) / (config.PINCH_MAX_DISTANCE - config.PINCH_MIN_DISTANCE)
        brush_size = int(normalized_span * (config.MAX_BRUSH_SIZE - config.MIN_BRUSH_SIZE) + config.MIN_BRUSH_SIZE)
        return brush_size

    def get_index_position(self, lm_list):
        return (lm_list[8][1], lm_list[8][2]) if len(lm_list) > 0 else None

    def get_bounding_box(self, lm_list):
        if len(lm_list) == 0: return None
        x_coords = [pt[1] for pt in lm_list]
        y_coords = [pt[2] for pt in lm_list]
        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

    def close(self):
        self.hands.close()