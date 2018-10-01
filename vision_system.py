import fiducial.tracker
import yolo.tracker

import cv2
import zmq

'''
(some kind of) distance threshold
to switch from yolo system
to fiducial marker system
'''
distance_threshold = 20

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

context = zmq.Context()
server_socket = context.socket(zmq.PUB)
server_socket.bind("tcp://*:5556")

if __name__ == '__main__':
    yolo_marker = yolo.tracker.find_object()
    while True:
        '''
        yield yolo buoy distance
        if distance > distance threshold continue yolo else switch to fiducial system
        '''
        if next(yolo_marker)[2] > distance_threshold:
            print(next(yolo_marker))
        else:
            fiducial_marker = fiducial.tracker.find_marker()
            print("fiducial system running")
            print(next(fiducial_marker))



        
    
