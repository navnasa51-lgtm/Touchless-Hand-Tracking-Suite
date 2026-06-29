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

## 🛠️ System Architecture & How It Works

The codebase is built on an asynchronous, decoupled, modular pipeline. This architecture ensures that heavy I/O operations (like writing video data to disk) and deep learning inferences (like OCR parsing) execute on separate worker threads, maintaining a high and stable frame rate for the camera capture loop.
