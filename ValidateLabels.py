import numpy as np
import cv2

from Classes import ImgReader, CubeBase, ColorReader

condition='dark'
picture_path='./pictures/'+condition+'/'
label_name='./labels/'+condition+'_label.npy'
feature_file='./labels/'+condition+'_feature.csv'
roi_path=picture_path+'rois/'
cv2.namedWindow("img")
counter = 0 
img_reader=ImgReader(picture_path,label_name)
cube = CubeBase()
img = img_reader.update(counter)
color_reader=ColorReader(feature_file)
color_img = color_reader.update()
counter+=1   

while True:
    # hist=calSoftHist(img_reader.colors[count])
    # drawHist(hist)
    cv2.imshow('img',img)
    cv2.imshow('color_img',color_img)
    key = cv2.waitKey(1)
    if key == 27:   
        break
    if (key == ord('n')):
        print('group is %d'%(counter))
        img = img_reader.update(counter)
        color_img = color_reader.update()
        counter+=1