import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import timeit
import socket
import vision_system

options = {
    'model': './yolo/cfg/tiny-yolo-voc-1c.cfg',
    'load': 1375,
    'threshold': 0.1,
}

tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]

def find_object():
    print("YOLO SYSTEM UP ##########################")
    while True:
        ret, frame = vision_system.capture.read()
        if ret:
            results = tfnet.return_predict(frame)
            for color, result in zip(colors, results):
                tl = (result['topleft']['x'], result['topleft']['y'])

                midpointX = (result['topleft']['x'] + result['bottomright']['x'])/2 
                midpointY = (result['topleft']['y'] + result['bottomright']['y'])/2

                br = (result['bottomright']['x'], result['bottomright']['y'])

                raw_distance = round(result['topleft']['x'] + result['bottomright']['x'], 1)

                label = result['label']
                confidence = result['confidence']

                vision_system.server_socket.send("x:{}, y:{}, distance:{}".format(midpointX, midpointY, raw_distance).encode())

                yield midpointX, midpointY, raw_distance
