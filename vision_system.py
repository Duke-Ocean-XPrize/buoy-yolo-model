import fiducial.tracker
import yolo.tracker
import cv2

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if __name__ == '__main__':
   yolo.tracker.find_object()
   fiducial.tracker.find_marker()