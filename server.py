
import socket
#import control.movement
 
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

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
    x_coord = float(data_list[0])
    y_coord = float(data_list[1])
    z_coord = float(data_list[2])
    print("x_coord {}".format(x_coord))
    print("y_coord {}".format(y_coord))
    print("z_coord {}".format(z_coord))

    '''
    if x_coord > center_threshold and x_coord < center_threshold:
                land()
    elif y_coord < center_threshold and y_coord < center_threshold:
            left(pid_transform(data))
    '''
conn.close()
