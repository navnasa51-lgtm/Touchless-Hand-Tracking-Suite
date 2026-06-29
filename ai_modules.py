"""
=========================================================
AI MODULES (Thread-Safe Operations)
Touchless Hand Tracking Suite V4+
=========================================================
"""

import cv2
import numpy as np
import easyocr
import os
from datetime import datetime
import config

class AIProcessor:
    def __init__(self):
        # Initialized once; thread-safe execution via localized runtime calls
        self.reader = easyocr.Reader(config.OCR_LANGUAGES, gpu=config.OCR_GPU)

    def preprocess_for_ocr(self, canvas):
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return cv2.morphologyEx(cv2.bitwise_not(thresh), cv2.MORPH_CLOSE, np.ones((2,2), np.uint8))

    def extract_text(self, canvas):
        try:
            processed = self.preprocess_for_ocr(canvas)
            results = self.reader.readtext(processed, detail=0)
            return " ".join(results) if results else "No Text Detected"
        except Exception as e:
            return f"OCR Error: {str(e)}"

    def recognize_shapes(self, canvas):
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shape_canvas = np.zeros_like(canvas)
        for cnt in contours:
            if cv2.contourArea(cnt) < config.MIN_SHAPE_AREA:
                continue

            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, config.CONTOUR_APPROX_FACTOR * perimeter, True)
            x, y, w, h = cv2.boundingRect(approx)

            if len(approx) == 3:
                cv2.drawContours(shape_canvas, [approx], -1, (0, 255, 0), 4)
                cv2.putText(shape_canvas, "Triangle", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            elif len(approx) == 4:
                aspect_ratio = w / float(h)
                label = "Square" if 0.95 <= aspect_ratio <= 1.05 else "Rectangle"
                cv2.rectangle(shape_canvas, (x, y), (x + w, y + h), (255, 0, 0), 4)
                cv2.putText(shape_canvas, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            elif len(approx) > 7:
                center = (x + w // 2, y + h // 2)
                radius = int(max(w, h) / 2)
                cv2.circle(shape_canvas, center, radius, (0, 0, 255), 4)
                cv2.putText(shape_canvas, "Circle", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.drawContours(shape_canvas, [cnt], -1, (255, 255, 255), 2)
        return shape_canvas

    def save_screenshot(self, frame):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(config.SCREENSHOT_FOLDER, f"screenshot_{timestamp}.png")
            cv2.imwrite(filename, frame)
            return filename
        except Exception:
            return None

    def run_ai_pipeline(self, canvas_layer):
        # Encapsulated workflow execution designed for threaded invokes
        shape_layer = self.recognize_shapes(canvas_layer)
        detected_text = self.extract_text(canvas_layer)
        merged_output = cv2.addWeighted(canvas_layer, 0.5, shape_layer, 1.0, 0)
        return merged_output, detected_text