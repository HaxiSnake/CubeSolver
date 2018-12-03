import numpy as np
import cv2

from Classes import ImgReader, CubeBase, ColorReader

# conditions=["cube1_dark","cube1_light","cube2_light","cube2_right_light","cube2_up_light"]
conditions=["cube2_light"]
feature="hsv"
for condition in conditions:
    picture_path='./pictures/'+condition+'/'
    label_name='./labels/'+condition+'_label.npy'
    feature_file='./labels/'+condition+'_'+feature+'_feature.csv'
    roi_path=picture_path+'rois/'
    print("The condition is %s"%(condition))
    cv2.namedWindow("img")
    counter = 0 
    img_reader=ImgReader(picture_path,label_name)
    cube = CubeBase()
    img = img_reader.update(counter)
    color_reader=ColorReader(feature_file)
    color_img = color_reader.update(counter)
      

    while True:
        # hist=calSoftHist(img_reader.colors[count])  
        # drawHist(hist)
        cv2.imshow('img',img)
        cv2.imshow('color_img',color_img)
        key = cv2.waitKey(1)
        if key == 27:   
            break
        if (key == ord('n')):
            try:
                counter+=1
                img = img_reader.update(counter)
                color_img = color_reader.update(counter)
                print('group is %d'%(counter))
            except:
                print("condition %s over"%(condition))
                break
        if (key == ord('N')):
            try:
                counter-=1
                img = img_reader.update(counter)
                color_img = color_reader.update(counter)
                print('group is %d'%(counter))
            except:
                counter=0
                img = img_reader.update(counter)
                color_img = color_reader.update(counter)
                print('group is %d'%(counter))
                