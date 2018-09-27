import fiducial.tracker
import yolo.tracker

threshold = 540

if __name__ == '__main__':
    yolo_marker = yolo.tracker.find_object()
    while True:
        if next(yolo_marker)[2] < threshold:
            print(next(yolo_marker))
        else:
            fiducial_marker = fiducial.tracker.find_marker()
            print("fiducial system running")
            print(next(fiducial_marker))



        
    
