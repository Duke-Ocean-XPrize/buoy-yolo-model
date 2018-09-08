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
FRAME_HEIGHT = 1080
FRAME_WIDTH = 1920
options = {
    'model': 'cfg/tiny-yolo-voc-1c.cfg',
    'load': 1375,
    'threshold': 0.1,
}
colors = [tuple(np.random.randint(low=0, high=256, size=3)) for _ in range(10)]

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
    if(movement_vectors[0] < 0):
        result_strings[0] = "go left {}".format(movement_vectors[0])
    else:
        result_strings[0] = "go right {}".format(movement_vectors[0])
    if(movement_vectors[1] < 0):
        result_strings[1] = "go up {}".format(movement_vectors[1])
    else:
        result_strings[1] = "go down {}".format(movement_vectors[1])

#Main program loop
while True:
    s.send('HTTP/1.0 200 OK\n')
    s.send('Content-Type: text/html\n')
    s.send('\n') # header and body should be separated by additional newline
    #Read frame-date from VideoCapture object
    capture_successful, frame = capture.read()
    if capture_successful:
        results = tfnet.return_predict(frame)
        for color, result in zip(colors, results):
            #Setting variables for the top-left and bottom-right points (x, y) of result border-box
            borderbox_topleft = (result['topleft']['x'], result['topleft']['y'])
            borderbox_bottomright = (result['bottomright']['x'], result['bottomright']['y'])

            #Calculating midpoint on frame
            borderbox_midpoint = (borderbox_topleft[0] + borderbox_bottomright[0])/2, result['topleft']['y'] + result['bottomright']['y'])/2)

            '''
            Calculating movement distances (in pixels) required to center border-box on frame.
            We can try to calibrate movement velocities left and right based on these numbers.
            There would of course be some range of acceptable valuables for x and y.
            '''
            frame_center = (np.floor(FRAME_WIDTH/2), np.floor(FRAME_HEIGHT/2))
            movement_vectors = (frame_center[0] - borderbox_midpoint[0], frame_center[1] - borderbox_midpoint[1])

            print("midpoint ({},{})".format(borderbox_midpoint[0], borderbox_midpoint[1]))
            print("movement-vectors: {}".format(movement_vectors))

            s.send("<html><body><h1>{}</h1></body></html>".format(movement_vectors))

            label = result['label']
            confidence = result['confidence']
            text = '{}: {:.0f}%'.format(label, confidence * 100)
            frame = cv2.rectangle(frame, borderbox_topleft, borderbox_bottomright, color, 5)
            frame = cv2.putText(frame, text, borderbox_topleft, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            text_directions = determine_direction(movement_vectors)
            frame = cv2.putText(frame, text_directions[0], (20, 155), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            frame = cv2.putText(frame, text_directions[1], (20, 55), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            if(movement_vectors[0] < 25 and movement_vectors[1] < 25):
                frame = cv2.putText(frame, "LANDING PAD CENTERED", (20, 300), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('frame', frame)
    else:
        #No midpoint found due to failed frame-capture
        s.send("<html><body><h1>{}</h1></body></html>".format("Frame not captured"))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
s.close()
capture.release()
cv2.destroyAllWindows()
