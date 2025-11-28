# Spider Bot: Advanced Autonomous Vision & Navigation System

**Author**: [Your Name/Organization]  
**Date**: November 2025  
**Version**: 2.0.0

---

## 1. Abstract

The **Spider Bot Vision System** is a comprehensive software framework designed to empower autonomous robotic platforms with advanced perception capabilities. By integrating state-of-the-art computer vision models (YOLOv8) with multi-sensor fusion (Ultrasonic & Thermal), this system provides real-time object detection, distance estimation, and environmental mapping. The project aims to bridge the gap between high-level AI decision-making and low-level hardware control, facilitating applications in search and rescue, surveillance, and autonomous navigation.

## 2. Introduction

In the realm of autonomous robotics, situational awareness is paramount. Traditional systems often rely on singular modalities—either visual or range-based data—limiting their effectiveness in complex environments. This project proposes a **Multi-Modal Perception Engine** that synergizes:
*   **RGB Vision**: For semantic understanding and object classification.
*   **Thermal Imaging**: For heat signature detection in low-visibility conditions.
*   **Ultrasonic Sensing**: For precise proximity measurements and obstacle avoidance.

The software is architected as a modular, event-driven application, ensuring scalability and ease of maintenance.

## 3. System Architecture

The system follows a modular design pattern, decoupling data acquisition, processing, and visualization.

### 3.1. Core Modules

| Module | Description |
| :--- | :--- |
| **`modules.vision`** | Implements the `VisionSystem` class. Utilizes **YOLOv8** for real-time inference on RGB feeds and manages asynchronous thermal camera streams. |
| **`modules.comms`** | Manages hardware communication via **Serial (USB)** and **Bluetooth**. Implements thread-safe data buffers for sensor telemetry. |
| **`modules.visualizer`** | Provides real-time data visualization. Features a **Rolling Time-Series Graph** for distance metrics and a **Polar Radar Plot** for spatial awareness. |
| **`modules.utils`** | Contains configuration constants, calibration data, and mathematical utilities for monocular distance estimation. |

### 3.2. Data Flow
1.  **Acquisition**: Cameras and sensors capture raw data asynchronously.
2.  **Processing**: 
    *   RGB frames are passed through the YOLO neural network.
    *   Bounding boxes are analyzed to estimate distance using focal length heuristics.
    *   Ultrasonic data is parsed from the serial stream.
3.  **Visualization**: Processed frames and sensor data are rendered onto the GUI.
4.  **Control**: User inputs are translated into serial commands for the robotic chassis.

## 4. Methodology

### 4.1. Monocular Distance Estimation
Distance ($D$) is calculated using the pinhole camera model:
$$ D = \frac{W \times F}{P} $$
Where:
*   $W$ = Real-world width of the object (cm).
*   $F$ = Focal length of the camera (pixels).
*   $P$ = Apparent width of the object on the sensor (pixels).

### 4.2. Object Detection
The system employs **YOLOv8 (You Only Look Once)**, a state-of-the-art convolutional neural network, optimized for speed and accuracy. It is configured to detect a specific subset of classes relevant to the robot's operational context (e.g., persons, bottles, chairs).

## 5. Installation & Prerequisites

### 5.1. Hardware Requirements
*   PC with Python 3.8+ support.
*   USB Webcams (RGB & Thermal).
*   Arduino/Microcontroller (for Ultrasonic data & Motor control).

### 5.2. Software Dependencies
Install the required Python packages:

```bash
pip install opencv-python ultralytics pyserial pillow matplotlib numpy
```

## 6. Usage Guide

1.  **Launch the Application**:
    ```bash
    python main.py
    ```
2.  **Interface Overview**:
    *   **Sidebar**: Contains controls for system state, camera modes, and Bluetooth connectivity.
    *   **Main View**: Displays the live video feed (RGB/Thermal).
    *   **Dashboard**: Shows real-time sensor graphs and radar visualization.
3.  **Operation**:
    *   Select the COM port and click **Connect** to establish a link with the robot.
    *   Click **START SYSTEM** to begin the vision processing loop.
    *   Use the **Manual Control** grid to drive the robot.

## 7. Future Work

*   **SLAM Integration**: Implementing Simultaneous Localization and Mapping for true autonomy.
*   **Stereo Vision**: upgrading from monocular heuristics to depth-camera based ranging.
*   **Edge Deployment**: Optimizing the model to run directly on edge devices like the NVIDIA Jetson Nano.

---
*Generated for the Spider Bot Project.*
