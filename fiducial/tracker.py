import numpy as np
import cv2
import cv2.aruco as aruco
import glob
import socket
import vision_system

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('./fiducial/calib_images/*.jpg')

def find_marker():
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (7,6),None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)


    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

    print("FIDUCIAL SYSTEM UP ##########################")
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
            rvec, tvec,_ = aruco.estimatePoseSingleMarkers(corners[0], 0.05, mtx, dist) #Estimate pose of each marker and return the values rvet and tvec---different from camera coefficients
            #(rvec-tvec).any() # get rid of that nasty numpy value array error

            topleftX = corners[0][0][0][0]
            topleftY = corners[0][0][0][1]

            toprightX = corners[0][0][1][0]
            toprightY = corners[0][0][1][1]

            bottomleftX = corners[0][0][2][0]
            bottomlextY = corners[0][0][2][1]

            bottomrightX = corners[0][0][3][0]
            bottomrightY = corners[0][0][3][1]

            distance = tvec[0][0][2]
            

            midpointX = (topleftX  + bottomrightX)/2 
            midpointY = (topleftY + bottomrightY)/2

            #print("marker midpoint X: {}, Y: {}, distance".format(midpointX, midpointY, distance))
            vision_system.server_socket.send("{},{},{}".format(midpointX, midpointY, distance).encode())
    
            yield midpointX, midpointY, raw_distance