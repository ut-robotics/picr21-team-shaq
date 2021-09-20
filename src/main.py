import cv2
import time
import numpy as np
import threading
from copy import copy
#----------------------------
import config
import Frame
from vision import Capture
from Detection import Detector

def create_detectors():
    detectors = {}
    #color_lims = config.load("colors") # Detect whole config
    color_lims = { color: config.load("colors")[color] for color in ("dark_green", "orange") } # Choose which to detect
    for color in color_lims:
        detectors[color] = Detector(color_lims[color])
    return detectors

def main():
    try:
        # Initialize capture with a configured Pre-processor
        Processor = Frame.Processor()
        cap = Capture(Processor)

        detectors = create_detectors()
        # print(detectors)
        lock = threading.Lock()
        for color_key in detectors:
            detectors[color_key].start_thread(cap, lock)
        cap.start_thread()

        print(threading.active_count(), " are alive")
        print(threading.enumerate())
        
        while True:
            # Read detectors and capture
            frame = cap.get_frame()
            gr = detectors["dark_green"]
            orn = detectors["orange"]
            
            frame2 = copy(frame)
            gr.draw_entity(frame)
            orn.draw_entity(frame2)
            if frame is not None:
                cv2.imshow("Green", frame)
                cv2.imshow("Mask_green", gr.color_mask)

                cv2.imshow("Orange", frame2)
                cv2.imshow("Mask_orange", orn.color_mask)

            k = cv2.waitKey(1) & 0xFF
            if k == ord("q"):
                print('Closing program')
                cap.running = False
                cv2.destroyAllWindows()
                break
            time.sleep(0.05)
    except Exception as e:
        print(e)
        cv2.destroyAllWindows()
        cap.running = False

if __name__ == "__main__":
    main()
