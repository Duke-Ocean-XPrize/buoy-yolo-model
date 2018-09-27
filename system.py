import fiducial.tracker
import yolo.tracker

threshold = 540

if __name__ == '__main__':
    yolo_marker = yolo.tracker.find_object()
    while True:
        if yolo_marker.__next__()[2] < threshold:
            print(yolo_marker.__next__())
        else:
            fiducial_marker = fiducial.tracker.find_marker()
            print("fiducial system running")
            print(fiducial_marker.__next__())



        
    
