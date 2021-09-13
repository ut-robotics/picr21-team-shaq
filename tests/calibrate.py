import cv2
import numpy as np
from threading import Thread
import time
import json
import sys, os
from functools import partial
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config, Frame

def update_range(edge, channel, value):
    """
    Parameters:
        edge = "min" or "max"
        channel = 0, 1, 2 (H, S, V)
        value = new slider value
    """
    filters[edge][channel] = value

def create_trackbars():
    win_name = "Color detection control"
    cv2.namedWindow(win_name)
    #print("filters are", filters)
    cv2.createTrackbar("H lower", win_name, filters["min"][0], 255, partial(update_range, "min", 0))
    cv2.createTrackbar("S lower", win_name, filters["min"][1], 255, partial(update_range, "min", 1))
    cv2.createTrackbar("V lower", win_name, filters["min"][2], 255, partial(update_range, "min", 2))
    cv2.createTrackbar("H upper", win_name, filters["max"][0], 255, partial(update_range, "max", 0))
    cv2.createTrackbar("S upper", win_name, filters["max"][1], 255, partial(update_range, "max", 1))
    cv2.createTrackbar("V upper", win_name, filters["max"][2], 255, partial(update_range, "max", 2))

def thread_test():
    while thread_alive:
        print(filters)
        time.sleep(2)
    return

#cv2.createTrackbar('Kernel size', win_name, kernel, 101, updateKernel)

def main():
    global filters, thread_alive
    user_choice = "green" #input("Enter color: ")
    filters = config.load("colors")[user_choice]
    create_trackbars()
    cap = cv2.VideoCapture(0)
    Processor = Frame.Processor(filters)
    """  Start a new thread that periodically prints """
    thread_alive = True
    counter = Thread(target=thread_test)
    counter.start()
    #counter.join()
    while True:
        _, frame = cap.read()
        obj_mask = Processor.process_frame(frame)

        cv2.imshow("Detection", obj_mask)
        #mask = cv2.dilate(mask, kernel, iterations=2)
        #imageProcessing.getFieldArea(frame, cnts3)
        #cont = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            thread_alive = False
            print('Closing program')
            cap.release()
            cv2.destroyAllWindows()
            config.update(filters) 
            break

if __name__ == "__main__":
    main()