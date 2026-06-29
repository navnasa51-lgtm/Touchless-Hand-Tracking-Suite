# Touchless Hand Tracking Suite

![Development Status](https://img.shields.io/badge/Status-In_Development/Unfinished-orange)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![MediaPipe](https://img.shields.io/badge/Framework-MediaPipe-teal)

A modular, real-time computer vision application that converts standard webcam feeds into an interactive, touchless tool workspace. The suite features an isolated virtual drawing canvas (Whiteboard), a zero-latency operating system GUI cursor controller, non-blocking asynchronous session recording, and deep-learning-powered text/shape recognition.

---

## 🚧 Crucial Project Status Notice
> [!WARNING]
> **This project is UNFINISHED and requires further optimization.** > While the code has been decoupled into an Object-Oriented modular ecosystem to prevent state cross-contamination, additional development is required to achieve commercial-grade precision and stability.

### Current Optimization Needs & System Jitter:
* **UI Controller Fine-Tuning**: Mouse tracking currently relies on an Exponential Moving Average (EMA) smoothing filter. While this dampens sudden jumps, it still exhibits micro-jitters during steady-point hovering or deep mouse operations.
* **Writing Precision**: Drawing alphanumeric text or fine lines inside the Whiteboard mode can feel loose. The tracking loop needs more advanced regression algorithms (like a 1D Euro Filter or Double Exponential Smoothing) to truly mimic a physical stylus.
* **Gesture Boundary Overlap**: Quick semantic transitions can occasionally register false positives if the hand is partially angled away from the camera lens, breaking the threshold limits.

---

## 📁 Project Structure

The project is structured logically to keep feature states separated. Below is the directory tree layout:

```
touchless-hand-tracking-suite/
│
├── main.py                  # The Central Orchestration Layer & Runtime Loop
├── config.py                # Global System Parameters, Thresholds, and Constants
├── hand_tracker.py          # Core MediaPipe Wrapper & Landmark Extraction Engine
├── canvas_module.py         # Isolated Virtual Whiteboard & Alpha-Blending System
├── ui_controller_module.py  # Coordinate Interp & OS PyAutoGUI Mouse Driver
├── ai_modules.py            # Async Worker Pipeline for EasyOCR & Shape Detection
├── recorder.py              # Thread-Buffered IO Queue Video Recording System
│
├── recordings/              # Auto-generated directory containing saved .avi sessions
├── screenshots/             # Auto-generated directory containing saved frame snapshots
└── README.md                # Project Documentation and Usage Guide
```

### Core Subsystems:
1. **`main.py` (The Orchestration Layer)**: Initiates hardware resources, reads global settings, captures input frames, monitors keyboard event overrides, and safely handles mode switching.
2. **`hand_tracker.py` (The Vision Engine)**: Utilizes the MediaPipe framework to extract 21 spatial hand landmark coordinates. It dynamically evaluates whether individual fingers are open or closed.
3. **`canvas_module.py` (The Virtual Whiteboard Subsystem)**: Encapsulates its own isolated pixel canvas layer matrix. It processes brush drawing vectors (`xp, yp`), handles palette color selections, and applies alpha-blending logic.
4. **`ui_controller_module.py` (The OS Automation Engine)**: Linearly interpolates raw video frame coordinates into the system's absolute display resolution using `numpy.interp`. It overrides frame delays (`pyautogui.PAUSE = 0`) for rapid cursor response.
5. **`ai_modules.py` (The Deep Learning Pipeline)**: Implements adaptive thresholding paired with an `EasyOCR` network instance. It processes text and shape extractions inside an asynchronous background thread.
6. **`recorder.py` (Threaded Video Writer)**: Offloads heavy video block encoding (`cv2.VideoWriter`) to a frame buffer, keeping frame drops to zero during recording sessions.

---

## 🎨 Semantic Gesture Reference Map

To prevent tracking drops caused by natural human hand relaxation, the application relies on **Semantic Mapping**. Instead of matching exact, rigid binary arrays, it evaluates only the core fingers required for a gesture while completely ignoring secondary fingers (like the thumb) during drawing actions.

| Gesture Appearance | Knuckle Configuration Array | Triggered Functional Sub-Routine |
| :--- | :--- | :--- |
| **Pure Pointing** | Index: `UP` <br> Middle/Ring/Pinky: `DOWN` <br> *Thumb: Ignored* | **Whiteboard Mode**: Continuous Line Drawing / Writing.<br>**UI Controller Mode**: Mirrors Hand to Mouse Cursor. |
| **Dual Pointing** | Index: `UP`, Middle: `UP` <br> Ring/Pinky: `DOWN` <br> *Thumb: Ignored* | **Whiteboard Mode**: Color/Tool Palette Selection (Hover over header boxes). |
| **Triple Pointing** | Index: `UP`, Middle: `UP`, Ring: `UP` <br> Pinky: `DOWN` <br> *Thumb: Ignored* | **Whiteboard Mode**: Fast Chord Eraser (Clears drawn paths instantly). |
| **Open Hand** | Index, Middle, Ring, Pinky: `UP` <br> *Thumb: Ignored* | **Global Action**: Instant Canvas Matrix Flush (Clears the entire board). |
| **Closed Fist** | Index, Middle, Ring, Pinky, Thumb: `DOWN` | **Global Action**: Triggers Asynchronous Deep Learning AI OCR Pipeline. |

* **Pinch Click Interaction**: When active in `UI_CONTROLLER` mode, checking the physical Euclidean distance between the tip of your thumb and the tip of your index finger against `CLICK_THRESHOLD` generates native OS click actions.

---

## 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/touchless-hand-tracking-suite.git](https://github.com/YOUR_USERNAME/touchless-hand-tracking-suite.git)
   cd touchless-hand-tracking-suite
