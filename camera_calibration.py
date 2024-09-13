import cv2
def setup_camera():
    vidcap = cv2.VideoCapture(0)
    while vidcap.isOpened():
            _, i = vidcap.read()
            cv2.imshow("processed_section", i)
            cv2.waitKey(10)

setup_camera()