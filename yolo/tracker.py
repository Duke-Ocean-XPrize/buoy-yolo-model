import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import timeit
import socket

midpointX = 0
midpointY = 0

TCP_IP = '127.0.0.1'
TCP_PORT = 5006
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

options = {
    'model': './yolo/cfg/tiny-yolo-voc-1c.cfg',
    'load': 1375,
    'threshold': 0.1,
}

tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def find_object():
    while True:
        ret, frame = capture.read()
        if ret:
            results = tfnet.return_predict(frame)
            for color, result in zip(colors, results):
                tl = (result['topleft']['x'], result['topleft']['y'])

                midpointX = (result['topleft']['x'] + result['bottomright']['x'])/2 
                midpointY = (result['topleft']['y'] + result['bottomright']['y'])/2

                br = (result['bottomright']['x'], result['bottomright']['y'])

                label = result['label']
                confidence = result['confidence']

                s.send("x:{}, y:{}".format(midpointX, midpointY).encode())

        else:
            print("bouy midpoint X: n, Y: n")
            s.send(b"/n/n/n")
