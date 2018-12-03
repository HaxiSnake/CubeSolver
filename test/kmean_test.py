import numpy as np
import cv2

from Classes import ImgReader, CubeBase, ValidateClass, ColorReader

condition='light'
picture_path='./pictures/'+condition+'/'
label_name='./labels/'+condition+'_label.npy'
feature_file='./labels/'+condition+'_feature.csv'
# cv2.namedWindow("img")
counter = 0 
#img_reader
img_reader=ImgReader(picture_path,label_name)
img = img_reader.update(counter)
#cube
cube = CubeBase()
result=cube.test(img)
result_img = cube.drawResult()
#color_reader
color_reader=ColorReader(feature_file)
color_img = color_reader.update()
#Verifier
verifier = ValidateClass()
verifier.validate(counter,result,color_reader.labels)
verifier.showResult()
counter+=1
cv2.imshow('img',img)
cv2.imshow('result',result_img)   

while True:
    key = cv2.waitKey(1)
    if key == 27:   
        break
    if (key == ord('n')):
        counter+=1
cv2.destroyAllWindows()


