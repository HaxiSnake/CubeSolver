import numpy as np
import cv2
from Classes import ColorReader
# conditions=['light','dark']
conditions=["cube1_dark","cube1_light","cube2_light","cube2_right_light","cube2_up_light"]
feature="_hsv"
for condition in conditions:
    feature_file='./labels/'+condition+feature+'_feature.csv'
    center_name="./labels/"+condition+"_center.npy"
    color_reader=ColorReader(feature_file)
    center_dict={}
    counter=0
    while True:
        try:
            group,centers=color_reader.readCenter(counter)
            center_dict[group]=centers
            counter+=1
        except:
            break
    np.save(center_name,center_dict)
    print("%s is writen!"%(center_name))