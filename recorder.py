"""
=========================================================
SESSION RECORDER (Non-Blocking Concurrent Layout)
Touchless Hand Tracking Suite V4+
=========================================================
"""

import cv2
import os
import queue
import threading
from datetime import datetime
import config

class SessionRecorder:
    def __init__(self):
        self.recording = False
        self.writer = None
        self.current_file = None
        self.frame_queue = queue.Queue()
        self.worker_thread = None

    def start(self):
        if self.recording: return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_file = os.path.join(config.RECORDING_FOLDER, f"session_{timestamp}.avi")
        fourcc = cv2.VideoWriter_fourcc(*config.VIDEO_CODEC)

        self.writer = cv2.VideoWriter(
            self.current_file, fourcc, config.VIDEO_FPS,
            (config.CAM_WIDTH, config.CAM_HEIGHT)
        )

        self.recording = True
        self.worker_thread = threading.Thread(target=self._async_writer_loop, daemon=True)
        self.worker_thread.start()
        print(f"[RECORDER] Thread Spawned. Output target: {self.current_file}")

    def _async_writer_loop(self):
        while self.recording or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=0.05)
                if self.writer is not None:
                    self.writer.write(frame)
                self.frame_queue.task_done()
            except queue.Empty:
                continue

    def stop(self):
        if not self.recording: return
        self.recording = False

        if self.worker_thread:
            self.worker_thread.join()
            self.worker_thread = None

        if self.writer is not None:
            self.writer.release()
            self.writer = None
        print("[RECORDER] Asynchronous write cycles flushed and safely closed.")

    def toggle(self):
        self.stop() if self.recording else self.start()

    def write(self, frame):
        if self.recording:
            # Enqueue frame copies to avoid memory mutation between frame loops
            self.frame_queue.put(frame.copy())

    def draw_indicator(self, frame):
        if not self.recording: return frame
        cv2.circle(frame, (30, 80), 12, (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, "REC ASYNC", (50, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    def draw_filename(self, frame):
        if not self.recording or not self.current_file: return frame
        filename = os.path.basename(self.current_file)
        cv2.putText(frame, filename, (10, config.CAM_HEIGHT - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        return frame

    def release(self):
        self.stop()