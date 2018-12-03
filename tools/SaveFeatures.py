import numpy as np
import cv2

from Classes import ImgReader, CubeBase
conditions = ["cube1_dark","cube1_light","cube2_light","cube2_right_light","cube2_up_light"]
for condition in conditions:
    features="all"
    picture_path='./pictures/'+condition+'/'
    label_name='./labels/'+condition+'_label.npy'
    # feature_file='./labels/'+condition+'_'+features+'_feature.csv'
    feature_file='./labels/'+"feature_"+condition+'.csv'
    roi_path=picture_path+'rois/'
    cv2.namedWindow("img")
    counter = 0 
    img_reader=ImgReader(picture_path,label_name)
    cube = CubeBase()
    img = img_reader.update(counter)
    cube.saveFeatures(img,feature_file,counter,features)
    cv2.imwrite(roi_path+str(counter)+'.jpg',img)
    counter+=1
    try:
        while True:
            # hist=calSoftHist(img_reader.colors[count])
            # drawHist(hist)
            cv2.imshow('img',img)
            key = cv2.waitKey(1)
            if key == 27:   
                break
            if (key == ord('n')):
                print('save %d features'%(counter))
                img = img_reader.update(counter)
                cube.saveFeatures(img,feature_file,counter,features)
                cv2.imwrite(roi_path+str(counter)+'.jpg',img)
                counter+=1
    except:
        print("this end")
