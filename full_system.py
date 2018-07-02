import cv2
import cv2.aruco as aruco
import glob
from darkflow.net.build import TFNet
import numpy as np
import time
import timeit


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

cap = cv2.VideoCapture(0)

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('calib_images/*.jpg')


for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)
    #print(corners)
    #print(objpoints)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)


while True:
    stime = time.time()
    ret, frame = capture.read()
    if ret:
        results = tfnet.return_predict(frame)
        print(results)
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
                
        if not results:
            print("using fiducial")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
            parameters = aruco.DetectorParameters_create()

            #lists of ids and the corners beloning to each id
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            font = cv2.FONT_HERSHEY_SIMPLEX

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

                print("topleft  corner x {}".format(topleftX))
                print("topleft corner y {}".format(topleftY))

                print("topright corner x {}".format(toprightX))
                print("topright corner y {}".format(toprightY))

                print("bottomleft corner x {}".format(bottomleftX))
                print("bottomleft corner y {}".format(bottomlextY))

                print("bottomright corner x {}".format(bottomrightX))
                print("bottomright corner y {}".format(bottomrightY))

                print("distance {}".format(tvec[0][0][2]))

                midpointX = (topleftX  + bottomrightX)/2 
                midpointY = (topleftY + bottomrightY)/2

                print("midpoint X: {}, Y: {}".format(midpointX, midpointY))


                aruco.drawAxis(frame, mtx, dist, rvec[0], tvec[0], 0.1) #Draw Axis
                aruco.drawDetectedMarkers(frame, corners) #Draw A square around the markers


                ###### DRAW ID #####
                cv2.putText(frame, "Id: " + str(ids), (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
                    

            #print('{} -- {}'.format(label, confidence))
        cv2.imshow('frame', frame)
        #print('FPS {:.1f}'.format(1 / (time.time() - stime)))
        #print('[INFO] elapsed time: {:.2f}'.format(time.time() - stime))
        #print(label)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
