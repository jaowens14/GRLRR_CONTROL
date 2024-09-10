
import cv2

def main():
    vidcap = cv2.VideoCapture(2)
    i = 0
    if vidcap.isOpened():
        while vidcap.isOpened():
            success, image = vidcap.read()
            image = cv2.flip(image, 0)
            cv2.imshow("frame", image)
            cv2.waitKey(0)
            cv2.imwrite("images/frame"+str(i)+".png", image)
            i = i + 1


print(__name__)
if __name__ == "__main__":
   
    main()