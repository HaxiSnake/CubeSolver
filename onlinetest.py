import numpy as np
import cv2

from Classes import ImgReader, CubeBase, ValidateClass, ColorReader, CenterReader


class Controller():
    def __init__(self,condition='light'):
        self.condition=condition
        self.picture_path='./pictures/'+condition+'/'
        self.label_name='./labels/'+condition+'_label.npy'
        self.feature_file='./labels/'+condition+'_hsv_feature.csv'
        self.center_file='./labels/'+condition+'_center.npy'
        # self.counter=0
        self.img_reader=ImgReader(self.picture_path,self.label_name)
        self.center=CenterReader(self.center_file)
        self.cube=CubeBase()
        self.color_reader=ColorReader(self.feature_file)
        self.verifier=ValidateClass()
    def run(self,maxgroup=11):
        for i in range(maxgroup):
            # print("group:",i)
            img=self.img_reader.update(i)
            center=self.center.getCenter(i)
            # print(center)
            result=self.cube.onlineUpdate(img,center)
            
            self.color_reader.update(i)
            self.verifier.validate(i,result,self.color_reader.cur_labels)
        print("dataset:",self.condition)
        self.verifier.showResult(isALL=False)

# key="cube1_dark"
conditions={"cube1_dark":25,
            "cube1_light":26,
            "cube2_light":24,
            "cube2_right_light":23,
            "cube2_up_light":19}
for condition,group in conditions.items():
    main = Controller(condition)
    main.run(group)
