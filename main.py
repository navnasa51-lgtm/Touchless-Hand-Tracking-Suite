"""
=========================================================
MAIN RUNTIME ORCHESTRATOR
Touchless Hand Tracking Suite V5.0
=========================================================
"""

import cv2
import time
import threading
import config

from hand_tracker import HandTracker
from ai_modules import AIProcessor
from recorder import SessionRecorder

# Import newly separated standalone feature modules
from canvas_module import CanvasModule
from ui_controller_module import UiControllerModule

# Operational concurrency variables for background vision tasks
ai_worker_thread = None
ai_processing_lock = threading.Lock()
is_ai_running = False

def async_ai_worker(ai_processor, canvas_copy, callback):
    global is_ai_running
    processed_canvas, text = ai_processor.run_ai_pipeline(canvas_copy)
    callback(processed_canvas, text)
    with ai_processing_lock:
        is_ai_running = False

def main():
    global is_ai_running, ai_worker_thread
    print("[SYSTEM] Booting Modular Hand Tracking Ecosystem...")

    cap = cv2.VideoCapture(config.CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    # Initialize separate subsystems
    tracker = HandTracker()
    ai_engine = AIProcessor()
    recorder = SessionRecorder()

    whiteboard = CanvasModule()
    ui_mouse = UiControllerModule()

    mode = "WHITEBOARD"
    extracted_text = ""
    last_ai_time = 0
    p_time = time.time()

    def handle_ai_results(updated_canvas, text_found):
        nonlocal extracted_text
        whiteboard.canvas = updated_canvas
        extracted_text = text_found
        print("[AI CALLBACK] Asynchronous analytical models parsed effectively.")

    print("\nSystem Active. Keyboard Inputs:")
    print("  M : Toggle Engine Mode (WHITEBOARD <-> UI_CONTROLLER)")
    print("  R : Toggle Non-Blocking Recording Engine")
    print("  S : Export Snapshot Output to Storage")
    print("  Q : Kill Execution Thread Pipeline\n")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Mirror frame immediately for intuitive, natural interaction
        frame = cv2.flip(frame, 1)

        # Analyze hand configurations
        tracker.find_hands(frame)
        lm_list = tracker.get_landmarks(frame)

        if len(lm_list) > 0:
            fingers = tracker.fingers_up(lm_list)
            index_pos = tracker.get_index_position(lm_list)
            thumb, index, middle, ring, pinky = fingers[0], fingers[1], fingers[2], fingers[3], fingers[4]

            # GLOBAL GESTURE: CLEAR CANVAS (All fingers extended except thumb)
            if index == 1 and middle == 1 and ring == 1 and pinky == 1:
                whiteboard.clear_canvas()
                extracted_text = ""
                cv2.putText(frame, "CANVAS CLEARED", (400, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # GLOBAL GESTURE: ASYNC AI RECOGNITION (Fist Gesture)
            elif thumb == 0 and index == 0 and middle == 0 and ring == 0 and pinky == 0:
                now = time.time()
                if now - last_ai_time > config.AI_TRIGGER_COOLDOWN:
                    with ai_processing_lock:
                        if not is_ai_running:
                            is_ai_running = True
                            last_ai_time = now
                            ai_worker_thread = threading.Thread(
                                target=async_ai_worker,
                                args=(ai_engine, whiteboard.canvas.copy(), handle_ai_results),
                                daemon=True
                            )
                            ai_worker_thread.start()

            # RUN MODULE BASED ON MODE SELECTION
            if mode == "WHITEBOARD":
                frame = whiteboard.process_interaction(frame, lm_list, fingers, index_pos)
            elif mode == "UI_CONTROLLER":
                ui_mouse.process_interaction(tracker, lm_list, fingers, index_pos)
        else:
            # If no hands are visible, reset tracking positions to avoid jumps when hands reappear
            whiteboard.reset_tracking()
            ui_mouse.reset_tracking()

        # Render On-Screen Displays (OSD) and operational feedback
        if is_ai_running:
            cv2.putText(frame, "AI ANALYSIS RUNNING...", (config.CAM_WIDTH - 380, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.WARNING_COLOR, 2)

        if extracted_text:
            cv2.putText(frame, f"OCR: {extracted_text[:60]}", (20, config.CAM_HEIGHT - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, config.SUCCESS_COLOR, 2)

        # Performance calculations
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.TEXT_COLOR, 2)
        cv2.putText(frame, f"Mode: {mode}", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.WARNING_COLOR, 2)

        if mode == "WHITEBOARD" and config.ENABLE_DYNAMIC_BRUSH and len(lm_list) > 0:
            cv2.putText(frame, f"Brush: {whiteboard.brush_size}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.TEXT_COLOR, 2)

        # Stream frames to the background recording queue
        frame = recorder.draw_indicator(frame)
        frame = recorder.draw_filename(frame)
        recorder.write(frame)

        cv2.imshow(config.WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('m'):
            # Clear historical coordinates when switching modes to avoid input jumps
            whiteboard.reset_tracking()
            ui_mouse.reset_tracking()
            mode = "UI_CONTROLLER" if mode == "WHITEBOARD" else "WHITEBOARD"
        elif key == ord('r'):
            recorder.toggle()
        elif key == ord('s'):
            filename = ai_engine.save_screenshot(frame)
            if filename:
                print(f"[CAPTURE] Snapshot saved to: {filename}")

    # Safely close streaming threads and windows
    recorder.release()
    tracker.close()
    cap.release()
    cv2.destroyAllWindows()
    print("[SYSTEM] Shutdown completed.")

if __name__ == "__main__":
    main()