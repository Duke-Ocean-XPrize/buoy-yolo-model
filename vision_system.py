import fiducial.tracker
import yolo.tracker

import cv2
import socket

'''
(some kind of) distance threshold
to switch from yolo system
to fiducial marker system
'''
distance_threshold = 20

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

TCP_IP = '127.0.0.1'
TCP_PORT = 5006
BUFFER_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((TCP_IP, TCP_PORT))

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



        
    
