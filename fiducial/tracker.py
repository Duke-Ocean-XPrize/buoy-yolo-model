import numpy as np
import cv2
import cv2.aruco as aruco
import glob
import socket
import vision_system
import math
import yaml

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

#Retrieving Distortion and 3D Matrices
try:
    calibration_file = open("fiducial/calibration_data.yaml", 'r')
    data_dict = yaml.load(calibration_file)
    mtx = data_dict["mtx"]
    dist = data_dict["dist"]
except Exception as e:
    print("Calibration Failure: {}".format(e))

def inversePerspective(rvec, tvec): 
    rvec, tvec = rvec.reshape((3, 1)), tvec.reshape((3, 1))
    R, _ = cv2.Rodrigues(rvec)
    R = np.matrix(R).T 
    invTvec = np.dot(-R, np.matrix(tvec)) 
    invRvec, _ = cv2.Rodrigues(R) 
    invTvec = invTvec.reshape((1, 3)) 
    invRvec = invRvec.reshape((1, 3)) 
    return invRvec.tolist(), invTvec.tolist()

def find_1D_midpoint(first_loc, second_loc):
    return (first_loc + second_loc) / 2
    
def floor_midpoint(midpoint):
    return (math.floor(midpoint[0]), math.floor(midpoint[1]))

def avg_of_vectors(vector_list):
    return sum(vector_list)/float(len(vector_list))


def find_marker():
    while True:
        ret, frame = vision_system.capture.read()
        # operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        parameters = aruco.DetectorParameters_create()

        #lists of ids and the corners beloning to each id
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)


        font = cv2.FONT_HERSHEY_SIMPLEX #font for displaying text (below)

        if np.all(ids != None):
            rvec, tvec,_ = aruco.estimatePoseSingleMarkers(corners, 0.10, mtx, dist) #Estimate pose of each marker and return the values rvet and tvec---different from camera coefficients
            inverse_rvec = []
            inverse_tvec = []

            for r, t in zip(rvec, tvec):
                aruco.drawAxis(frame, mtx, dist, r, t, 0.1) #Draw Axis
                i_rvec, i_tvec = inversePerspective(r[0], t[0])
                inverse_rvec.append(i_rvec)
                inverse_tvec.append(i_tvec)

            marker_midpoints = []
            for index, id in zip(range(len(ids)), ids):
                topleftX = math.floor(corners[index][0][0][0])
                topleftY = math.floor(corners[index][0][0][1])
                toprightX = math.floor(corners[index][0][1][0])
                toprightY = math.floor(corners[index][0][1][1])
                bottomrightX = math.floor(corners[index][0][2][0])
                bottomrightY = math.floor(corners[index][0][2][1])
                bottomleftX = math.floor(corners[index][0][3][0])
                bottomlextY = math.floor(corners[index][0][3][1])
                midpoint = polylabel([[[topleftX, topleftY], [toprightX, toprightY], [bottomrightX, bottomrightY], [bottomleftX, bottomlextY]]])
                ###### DRAW ID #####
                cv2.putText(frame, "Id: " + str(id), floor_midpoint(midpoint), font, 1, (0,255,0),2,cv2.LINE_AA)
                marker_midpoints.append([math.floor(midpoint[0]), math.floor(midpoint[1])])
                
            num_of_markers = len(marker_midpoints)
            visual_center_of_markers = (-1, -1)
            translational_vector = (-1, -1, -1)

            if num_of_markers == 0:
                pass
            elif num_of_markers == 1:
                visual_center_of_markers = floor_midpoint(marker_midpoints[0])
                translational_vector = (inverse_tvec[0][0][0], inverse_tvec[0][0][1], inverse_tvec[0][0][2])
            elif num_of_markers == 2:
                visual_center_of_markers = floor_midpoint((find_1D_midpoint(marker_midpoints[0][0], marker_midpoints[1][0]), find_1D_midpoint(marker_midpoints[0][1], marker_midpoints[1][1])))
                translational_vector = (find_1D_midpoint(inverse_tvec[0][0][0], inverse_tvec[1][0][0]), find_1D_midpoint(inverse_tvec[0][0][1], inverse_tvec[1][0][1]), find_1D_midpoint(inverse_tvec[0][0][2], inverse_tvec[1][0][2]))
            else:
                x_values = []
                y_values = []
                z_values = []
                for index in range(len(inverse_tvec[0])):
                    x_values.append(inverse_tvec[index][0][0])
                    y_values.append(inverse_tvec[index][0][1])
                    z_values.append(inverse_tvec[index][0][2])
                visual_center_of_markers = floor_midpoint(polylabel([marker_midpoints]))
                translational_vector = (avg_of_vectors(x_values), avg_of_vectors(y_values), avg_of_vectors(z_values))

            vision_system.server_socket.send_string("{},{},{}".format(str(translational_vector[0])[:7], str(translational_vector[1])[:7], str(translational_vector[2])[:7]).encode())
    
            yield str(translational_vector[0])[:7], str(translational_vector[1])[:7], str(translational_vector[2])[:7]