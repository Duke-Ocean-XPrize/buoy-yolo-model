import zmq
#import control.movement

yolo_filter = "1"
fiducial_filter = "2"
yolo_port = 5555
fiducial_port = 5556
 
#  Socket to talk to server
context = zmq.Context()

# yolo globals
viewport_x_size = 640
viewport_y_size = 480

x_center_threshold = viewport_x_size/2
y_center_threshold = viewport_y_size/2
drop_thresh = 30

socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:{}".format(yolo_port))
socket.connect("tcp://localhost:{}".format(fiducial_port))
socket.setsockopt_string(zmq.SUBSCRIBE, yolo_filter)
socket.setsockopt_string(zmq.SUBSCRIBE, fiducial_filter)


def connect_vision():
    vision_data = socket.recv_string()
    vision_id, midpointX, midpointY, raw_distance = vision_data.split(",")
    midpointX = float(midpointX)
    midpointY = float(midpointY)
    raw_distance = float(raw_distance)
    print("{},{},{},{}".format(vision_id,midpointX, midpointY, raw_distance))

    x_dist = abs(midpointX - viewport_x_size)
    y_dist = abs(midpointY - viewport_y_size)

    if midpointX > x_center_threshold:
        print("move RIGHT")
    else:
        print("move LEFT")

    if midpointY < x_center_threshold:
        print("move DOWN")
    else:
        print("move UP")

    if x_dist > drop_thresh and y_dist < drop_thresh:
        print("I'M LANDING")
    
    return raw_distance

while True:
    connect_vision()
        

   