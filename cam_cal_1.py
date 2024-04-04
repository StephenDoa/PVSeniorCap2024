import cv2 as cv
import time
import numpy as np

cv.namedWindow("Image Feed")
cv.moveWindow("Image Feed", 159, -25)

cap = cv.VideoCapture(0)

#setup camera
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480) #these frames provide accuracy without slowdown
cap.set(cv.CAP_PROP_FPS, 40)

prev_frame_time = time.time()

cal_image_count = 0
frame_count = 0

while True:
    ret, frame = cap.read() #reads camera frame
   
    #processing code here
    frame_count += 1
   
    #save images to file cal_image.jpg
    if frame_count == 30:
        #cv.imwrite("cal_image_" + str(cal_image_count) + ".jpg", frame)
        cal_image_count += 1
        frame_count = 0
   
    #calculate the FPS and display on frame
    new_frame_time = time.time()
    fps = 1/(new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    cv.putText(frame, "FPS " + str(int(fps)), (10, 40), cv.FONT_HERSHEY_PLAIN, 3, (100, 255, 0), 2, cv.LINE_AA)
   
    cv.imshow("Image Feed", frame)
   
    #--- use "q" to quit
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"): break
   
cap.release()
cv.destroyAllWindows()
