import numpy as np
import cv2

from Classes import ImgReader, CubeBase, ValidateClass, ColorReader


class Controller():
    def __init__(self,condition='light'):
        self.picture_path='./pictures/'+condition+'/'
        self.label_name='./labels/'+condition+'_label.npy'
        self.feature_file='./labels/'+condition+'_feature.csv'
        # self.counter=0
        self.img_reader=ImgReader(self.picture_path,self.label_name)
        self.cube=CubeBase()
        self.color_reader=ColorReader(self.feature_file)
        self.verifier=ValidateClass()
    def run(self,maxgroup=11):
        for i in range(maxgroup):
            img=self.img_reader.update(i)
            # result=self.cube.update(img)
            result=self.cube.test(img)
            self.color_reader.update()
            self.verifier.validate(i,result,self.color_reader.labels)
        self.verifier.showResult()

main = Controller('dark')
main.run()