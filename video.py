#!/Users/Zapata/anaconda/lib/python2.7
import cv2
from darkflow.net.build import TFNet
import numpy as np
import socket

'''INTEGRATION CODE
connect_string = serial.Serial('/dev/ttyUSB0') #Used to connect serially with the drone via drone-kit (gives access to camera and perhaps localhost on drone board)
try:
    vehicle = connect(connect_string, heartbeat_timeout=1) #Connects to the vehicle and returns vehicle object. Exception thrown if heartbeat not received in 1 second.
exception:
    print("VEHICLE CONNECTION DID NOT WORK")
'''

#Setting variables
TCP_IP = '127.0.0.1' #Currently set to localhost
TCP_PORT = 5005
BUFFER_SIZE = 1024
FRAME_HEIGHT = 640
FRAME_WIDTH = 480
options = {
    'model': 'cfg/tiny-yolo-voc-1c.cfg',
    'load': 1375,
    'threshold': 0.1,
}

colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]

#Opening socket connection on given IP and Port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

#Instantiating TensorFlow net
tfnet = TFNet(options)

#Starting video capturing
capture = cv2.VideoCapture(0) #Beginning video capture with camera with device-index 0
capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

#Helper methods
def determine_direction(movement_vectors):
    result_strings = ("", "")
    result_strings = list(result_strings)
    if(movement_vectors[0] < 0):
        result_strings[0] = "go right"
    else:
        result_strings[0] = "go left"
    if(movement_vectors[1] < 0):
        result_strings[1] = "go up"
    else:
        result_strings[1] = "go down"
    return result_strings

s.send('HTTP/1.0 200 OK\n'.encode())
s.send('Content-Type: text/html\n'.encode())
s.send('\n'.encode()) # header and body should be separated by additional newline
#Read frame-date from VideoCapture object

#Main program loop
while True:
    capture_successful, frame = capture.read()
    if capture_successful:
        results = tfnet.return_predict(frame)
        for color, result in zip(colors, results):
            #Setting variables for the top-left and bottom-right points (x, y) of result border-box
            borderbox_topleft = (result['topleft']['x'], result['topleft']['y'])
            borderbox_bottomright = (result['bottomright']['x'], result['bottomright']['y'])

            #Calculating midpoint on frame
            borderbox_midpoint = ((borderbox_topleft[0] + borderbox_bottomright[0])/2, (borderbox_topleft[1] + borderbox_bottomright[1])/2)
            borderbox_dimensions = (borderbox_bottomright[0] - borderbox_topleft[0], borderbox_bottomright[1] - borderbox_topleft[1])
            '''
            Calculating movement distances (in pixels) required to center border-box on frame.
            We can try to calibrate movement velocities left and right based on these numbers.
            There would of course be some range of acceptable valuables for x and y.
            '''
            frame_center = (np.floor(FRAME_HEIGHT/2), np.floor(FRAME_WIDTH/2))
            movement_vectors = (frame_center[0] - borderbox_midpoint[0], borderbox_midpoint[1] - frame_center[1])

            print("midpoint ({},{})".format(borderbox_midpoint[0], borderbox_midpoint[1]))
            print("movement-vectors: {}".format(movement_vectors))
            print("frame_center: {}, {}".format(frame_center[0], frame_center[1]))

            s.send("<html><body><h1>{}</h1></body></html>".format(movement_vectors).encode())

            label = result['label']
            confidence = result['confidence']
            text = '{}: {:.0f}%'.format(label, confidence * 100)
            frame = cv2.rectangle(frame, borderbox_topleft, borderbox_bottomright, color, 5)
            frame = cv2.putText(frame, text, borderbox_topleft, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            text_directions = determine_direction(movement_vectors)
            if text_directions != None:
                frame = cv2.putText(frame, "{}: {}".format(text_directions[0], np.sign(movement_vectors[0])*(1 - np.round(borderbox_dimensions[0]/FRAME_HEIGHT, 3))), (0, 75), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                frame = cv2.putText(frame, "{}: {}".format(text_directions[1], np.sign(movement_vectors[1])*(1 - np.round(borderbox_dimensions[1]/FRAME_WIDTH, 3))), (0, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            frame = cv2.putText(frame, "midpoint: ({}, {})".format(borderbox_midpoint[0], borderbox_midpoint[1]), (20, 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            if(movement_vectors[0] < 15 and movement_vectors[1] < 15):
                frame = cv2.putText(frame, "BUOY CENTERED", (200, 440), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            break
        cv2.imshow('frame', frame)
    else:
        #No midpoint found due to failed frame-capture
        s.send("<html><body><h1>{}</h1></body></html>".format("Frame not captured").encode())

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
s.close()
capture.release()
cv2.destroyAllWindows()
