import zmq
#import control.movement
 
#  Socket to talk to server
context = zmq.Context()
yolo_socket = context.socket(zmq.SUB)
fiducial_socket = context.socket(zmq.SUB)

print("Connecting to servers…")
yolo_socket.connect("tcp://localhost:5556")
fiducial_socket.connect("tcp://localhost:5555")

yolo_filter = "1"
fiducial_filter = "2"

yolo_socket.setsockopt_string(zmq.SUBSCRIBE, yolo_filter)
fiducial_socket.setsockopt_string(zmq.SUBSCRIBE, fiducial_filter)

viewport_x_size = 640
viewport_y_size = 480


x_center_threshold = viewport_x_size/2
y_center_threshold = viewport_y_size/2

drop_thresh = 30
x_down_center_threshold = (viewport_x_size/2 - drop_thresh)
y_down_center_threshold = (viewport_y_size/2 - drop_thresh)

'''
            y_coord
                |
                |
            ---------
            |   |   |
            |   |   |
x_coord---------------------
            |   |   |
            |   |   |
            --------
                |
                |
'''


def pid_transform(x_coord, y_coord, distance):
    '''
    transform raw image coordinates to PID directional movements
    '''
    return data

 
while True:
    yolo_data = yolo_socket.recv_string()
    fiducial_data = fiducial_socket.recv_string()
    
    yolo_system_id, midpointX, midpointY, raw_distance = yolo_data.split(",")
    fiducial_system_id, midpointX, midpointY, raw_distance = fiducial_data.split(",")
    print(yolo_system_id)
    print(fiducial_system_id)
    try:
        x_coord = float(data_list[0])
        y_coord = float(data_list[1])
        z_coord = float(data_list[2])
        print("x_coord {}".format(x_coord))
        print("y_coord {}".format(y_coord))
        print("z_coord {}".format(z_coord))

        x_dist = abs(x_coord - 600)
        y_dist = abs(y_coord - 400)


        '''
        you need to fix these
        '''
        if x_coord > x_center_threshold:
            #move_left(pid_transform(data))
            print("move RIGHT")
        else:
            print("move LEFT")

        if y_coord < x_center_threshold:
            #move_rigth(pid_transform(data))
            print("move DOWN")
        else:
            print("move UP")

        if x_dist > drop_thresh and y_dist < drop_thresh:
            print("I'M LANDING")
    except:
        pass

conn.close()
