import socket
#import control.movement
 
TCP_IP = '127.0.0.1'
TCP_PORT = 5006
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

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

 
conn, addr = s.accept()
print('Connection address:', addr)
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    conn.send(data)  # echo

    #convert to list of coords
    data_string = data.decode("utf-8") 
    data_list = data_string.split(",")
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
