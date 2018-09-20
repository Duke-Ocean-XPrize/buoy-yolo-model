import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import timeit
import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5006
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

options = {
    'model': 'cfg/tiny-yolo-voc-1c.cfg',
    'load': 1375,
    'threshold': 0.1,
}

tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)



while True:
    stime = time.time()
    start = timeit.timeit()
    ret, frame = capture.read()
    if ret:

        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        the_marker = np.float32(gray)
            
        corners = cv2.goodFeaturesToTrack(the_marker, 100, 0.1, 10)
        corners = np.int0(corners)

        for corner in corners:
            x, y = corner.ravel()
            cv2.circle(frame,(x,y), 3, 255, -1)

        results = tfnet.return_predict(frame)
        for color, result in zip(colors, results):
            tl = (result['topleft']['x'], result['topleft']['y'])

            midpointX = (result['topleft']['x'] + result['bottomright']['x'])/2 
            midpointY = (result['topleft']['y'] + result['bottomright']['y'])/2

            distX = abs(midpointX - 600)
            distY = abs(midpointY - 400)
            
            raw_distance = round( (1-(result['topleft']['x'] + result['bottomright']['x'])), 1)
            print("raw distance: {}".format(raw_distance))

            br = (result['bottomright']['x'], result['bottomright']['y'])

            print("midpoint ({},{})".format(midpointX, midpointY))

            s.send("x:{}, y:{}".format(midpointX, midpointY).encode())

            label = result['label']
            confidence = result['confidence']
            text = '{}: {:.0f}%'.format(label, confidence * 100)
            frame = cv2.rectangle(frame, tl, br, color, 5)
            frame = cv2.putText(
                frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            if(midpointX < 600):
                frame = cv2.putText(
                frame, "go right {}".format(distX), (20, 155), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            else:
                frame = cv2.putText(
                frame, "go left {}".format(distX), (20, 155), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            if(midpointY < 400):
                frame = cv2.putText(
                frame, "go down {}".format(distY), (20, 55), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            else:
                frame = cv2.putText(
                frame, "go up {}".format(distY), (20, 55), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            if(distX < 25 and distY < 25):
                frame = cv2.putText(
                frame, "LANDING PAD CENTERED", (20, 300), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('frame', frame)
        cv2.imshow('corners', frame)

    else:
        print("midpoint X: n, Y: n")
        s.send(b"/n/n/n")
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
