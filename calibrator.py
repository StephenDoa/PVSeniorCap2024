import cv2 as cv
import glob
import numpy as np

cb_width = 7
cb_height = 7
cb_square_size = 26.3

#termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

#prepare object points e.g. (0, 0, 0), (1, 0, 0) ...
cb_3D_points = np.zeros((cb_width * cb_height, 3), np.float32)
cb_3D_points[:,:2] = np.mgrid[0:cb_width, 0:cb_height].T.reshape(-1, 2) * cb_square_size

#Arrays storing object points and image points from img's
list_cb_3d_points = [] #3d point in real world space
list_cb_2d_img_points = [] #2d points in img plane

list_images = glob.glob('*.jpg')

for frame_name in list_images:
    img = cv.imread(frame_name)
   
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
   
    #find chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7,7),None)
   
    #if found, add object points, image points (after refining)
    if ret == True:
        list_cb_3d_points.append(cb_3D_points)
       
        corners2 = cv.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        list_cb_2d_img_points.append(corners2)
       
        #Draw and display corners
        cv.drawChessboardCorners(img, (cb_width, cb_height), corners2,ret)
        cv.imshow('img',img)
        cv.waitKey(500)
       
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(list_cb_3d_points, list_cb_2d_img_points, gray.shape[::-1],None,None)
print("Calibration Matrix: ")
print(mtx)
print("Distortion: ", dist)

with open('camera_cal.npy', 'wb') as f:
    np.save(f, mtx)
    np.save(f, dist)