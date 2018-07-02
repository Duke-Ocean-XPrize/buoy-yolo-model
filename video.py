import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import timeit
import socket

#ser = serial.Serial('/dev/ttyUSB0')
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
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
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)



while True:
    stime = time.time()
    start = timeit.timeit()
    ret, frame = capture.read()
    if ret:
        results = tfnet.return_predict(frame)
        for color, result in zip(colors, results):
            tl = (result['topleft']['x'], result['topleft']['y'])
            #print("topleft x {}".format(result['topleft']['x']))
            #print("topleft y {}".format(result['topleft']['y']))

            midpointX = (result['topleft']['x'] + result['bottomright']['x'])/2 
            midpointY = (result['topleft']['y'] + result['bottomright']['y'])/2

            distX = abs(midpointX - 600)
            distY = abs(midpointY - 400)


            br = (result['bottomright']['x'], result['bottomright']['y'])
            #print("bottomright x {}".format(result['bottomright']['x']))
            #print("bottomright y {}".format(result['bottomright']['y']))

            print("midpoint ({},{})".format(midpointX, midpointY))

            #s.send("x:{}, y:{}".format(midpointX, midpointY).encode())
            s.send("{}/{}/{}".format(midpointX, midpointY).encode())


            end = timeit.timeit()
            print("latency???? in milliseconds {}".format((end - start)*1000))


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

            #print('{} -- {}'.format(label, confidence))
        cv2.imshow('frame', frame)
        #print('FPS {:.1f}'.format(1 / (time.time() - stime)))
        #print('[INFO] elapsed time: {:.2f}'.format(time.time() - stime))
        #print(label)
    else:
        print("midpoint X: n, Y: n")
        s.send(b"/n/n/n")
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
