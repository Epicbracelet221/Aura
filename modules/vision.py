import cv2
import threading
import queue
import time
import numpy as np
from PIL import Image
from ultralytics import YOLO
from .utils import KNOWN_WIDTHS, calculate_distance

class VisionSystem:
    def __init__(self, model_path="yolov8m.pt"):
        self.model = YOLO(model_path)
        self.running = False
        
        # RGB Camera
        self.cap = None
        self.frame_queue = queue.Queue(maxsize=1)
        
        # Thermal Camera
        self.cap_thermal = None
        self.thermal_queue = queue.Queue(maxsize=1)
        
        # Settings
        self.focal_length = 600.0
        self.target_class = "person"
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._process_rgb, daemon=True).start()
            threading.Thread(target=self._process_thermal, daemon=True).start()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.cap_thermal:
            self.cap_thermal.release()

    def set_focal_length(self, fl):
        self.focal_length = float(fl)

    def set_target_class(self, target):
        self.target_class = target

    def _process_rgb(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.start_time = time.time()
        self.frame_count = 0

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            frame = cv2.flip(frame, 1)

            results = self.model(frame, stream=True, verbose=False, conf=0.5)
            
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    label = self.model.names[cls]
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w_pixel = x2 - x1
                    
                    color = (0, 255, 0) # Green
                    dist_text = ""

                    if label in KNOWN_WIDTHS:
                        real_width = KNOWN_WIDTHS[label]
                        distance = calculate_distance(w_pixel, real_width, self.focal_length)
                        dist_text = f"{distance:.0f}cm"
                        
                        if distance < 30:
                            color = (0, 0, 255) # Red
                        elif distance < 60:
                            color = (0, 165, 255) # Orange
                        
                        if label == self.target_class:
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 3) # Cyan thick box
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    full_label = f"{label} {dist_text}"
                    cv2.putText(frame, full_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            self.frame_count += 1
            elapsed = time.time() - self.start_time
            if elapsed > 1:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.start_time = time.time()

            cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            
            if not self.frame_queue.empty():
                try: self.frame_queue.get_nowait()
                except: pass
            self.frame_queue.put(img_pil)

        self.cap.release()

    def _process_thermal(self):
        self.cap_thermal = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not self.cap_thermal.isOpened():
            self.cap_thermal = cv2.VideoCapture(2, cv2.CAP_DSHOW)
        
        while self.running:
            if self.cap_thermal and self.cap_thermal.isOpened():
                ret, frame = self.cap_thermal.read()
                if ret:
                    frame = cv2.resize(frame, (400, 300))
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    
                    if not self.thermal_queue.empty():
                        try: self.thermal_queue.get_nowait()
                        except: pass
                    self.thermal_queue.put(img_pil)
                else:
                    time.sleep(0.1)
            else:
                blank = np.zeros((300, 400, 3), np.uint8)
                cv2.putText(blank, "NO THERMAL CAM", (80, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                img_pil = Image.fromarray(blank)
                
                if not self.thermal_queue.empty():
                        try: self.thermal_queue.get_nowait()
                        except: pass
                self.thermal_queue.put(img_pil)
                time.sleep(0.5)
