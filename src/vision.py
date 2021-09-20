"""Create a thread here for reading camera frames with realsense2"""
import pyrealsense2
from threading import Thread
import cv2
import Frame

class Capture:
    def __init__(self, Processor=None):
        self.frame = None
        self.pf = None
        self.processor = Processor
        self.running = True
    
    def capture_thread(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            _, frame = cap.read() #(480, 640)
            self.frame = frame
            self.pf = self.pre_process(frame)
        cap.release()

    def pre_process(self, frame):
        # Create single pre-processed frame for all detectors
        return self.processor.pre_process(frame)
    
    def get_pf(self):
        return self.pf
    def get_frame(self):
        return self.frame

    def start_thread(self):
        Thread(name="Capture", target=self.capture_thread).start()
