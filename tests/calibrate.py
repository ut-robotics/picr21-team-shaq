import cv2
import numpy as np
import time
import json
import sys, os
from functools import partial
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config, Frame, vision
from threading import Thread

def update_range(edge, channel, value):
    """
    Parameters:
        edge = "min" or "max"
        channel = 0, 1, 2 (H, S, V)
        value = new slider value
    """
    filters[edge][channel] = value
    Processor.update_limits(filters)

def create_trackbars():
    win_name = "Set limits"
    cv2.namedWindow(win_name)
    cv2.createTrackbar("H lower", win_name, filters["min"][0], 255, partial(update_range, "min", 0))
    cv2.createTrackbar("S lower", win_name, filters["min"][1], 255, partial(update_range, "min", 1))
    cv2.createTrackbar("V lower", win_name, filters["min"][2], 255, partial(update_range, "min", 2))
    cv2.createTrackbar("H upper", win_name, filters["max"][0], 255, partial(update_range, "max", 0))
    cv2.createTrackbar("S upper", win_name, filters["max"][1], 255, partial(update_range, "max", 1))
    cv2.createTrackbar("V upper", win_name, filters["max"][2], 255, partial(update_range, "max", 2))

def thread_test():
    print(filters)
    time.sleep(2)
        
def main():
    global filters, Processor, thread_alive
    try:
        color = sys.argv[1]
    except:
        print("Color input required:\n\npython calibrate.py {color name}")
        sys.exit(2)
    color_config = config.load("colors")
    if color not in color_config.keys():
        print(f"Color '{color}' not found in config")
        sys.exit(2)
        
    filters = color_config[color]
    Processor = Frame.Processor(filters)
    create_trackbars()
    #cap = cv2.VideoCapture(0)
    cap = vision.Capture(Processor)
    cap.start_thread()

    """  Start a new thread that periodically prints """
    counter = Thread(target=thread_test, daemon=True)
    counter.start()
    #counter.join()

    win_name = f"Calibration for {color}"
    while True:
        #_, frame = cap.read() #(480, 640)
        frame = cap.get_color()
        obj_mask = Processor.process_frame(frame)#[0:240, 0:320])
        #print(obj_mask.shape)
        #cv2.imshow(win_name, frame)
        cv2.imshow(win_name, obj_mask)
        
        #mask = cv2.dilate(mask, kernel, iterations=2)
        #imageProcessing.getFieldArea(frame, cnts3)
        #cont = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            print('Closing program')
            cap.release()
            cv2.destroyAllWindows()
            config.update(color, filters) 
            break

if __name__ == "__main__":
    main()
