import zmq
#import control.movement

yolo_filter = "1"
fiducial_filter = "2"
 
#  Socket to talk to server
context = zmq.Context()

# yolo globals
viewport_x_size = 640
viewport_y_size = 480

x_center_threshold = viewport_x_size/2
y_center_threshold = viewport_y_size/2
drop_thresh = 30


def connect_fiducial():
    print("...Connected to fiducial")
    fiducial_socket = context.socket(zmq.SUB)
    fiducial_socket.connect("tcp://localhost:5556")
    fiducial_socket.setsockopt_string(zmq.SUBSCRIBE, fiducial_filter)
    fiducial_data = fiducial_socket.recv_string()
    fiducial_system_id, midpointX, midpointY, raw_distance = fiducial_data.split(",")

    print(fiducial_system_id)

def connect_yolo():
    yolo_socket = context.socket(zmq.SUB)
    yolo_socket.connect("tcp://localhost:5555")
    yolo_socket.setsockopt_string(zmq.SUBSCRIBE, yolo_filter)
    yolo_data = yolo_socket.recv_string()
    yolo_system_id, midpointX, midpointY, raw_distance = yolo_data.split(",")
    midpointX = float(midpointX)
    midpointY = float(midpointY)
    raw_distance = float(raw_distance)
    print("{},{},{},{}".format(yolo_system_id,midpointX, midpointY, raw_distance))

    x_dist = abs(midpointX - 600)
    y_dist = abs(midpointY - 400)

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
    if connect_yolo() > 800:
        connect_fiducial()
        

   