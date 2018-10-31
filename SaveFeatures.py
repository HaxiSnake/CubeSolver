import numpy as np
import cv2

from Classes import ImgReader, CubeBase

picture_path='./pictures/light/'
label_name='light_label.npy'

cv2.namedWindow("img")
counter = 0 
img_reader=ImgReader(picture_path,label_name)
img = img_reader.update(counter)
cube = CubeBase()

while True:
    # hist=calSoftHist(img_reader.colors[count])
    # drawHist(hist)
    key = cv2.waitKey(1)
    if key == 27:   
        break
    if (key == ord('n')):
        counter+=1
