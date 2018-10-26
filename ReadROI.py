import numpy as np
import cv2

picture_path='./pictures/light/'
label_name='light_label.npy'
class ImgReader():
    def __init__(self,picture_path,label_name,group=0):
        self._path =picture_path
        self._group=group
        self.pics=[]
        self.ROIS = None
        try:
            self.label_dic = np.load(label_name)
            self.label_dic = self.label_dic[()]
        except:
            self.label_dic = {}
            print("Can not find label file at %s"%(label_name))
        self.readPics(0)      
    def readPics(self,group):
        self.pics=[]
        self._group=group
        for i in range(3):
            name = self._path + str(group)+'_'+str(i)+'.jpg'
            img  = cv2.imread(name)
            if(img is None):
                print("Can not find picture at %s"%(name))
                img = cv2.imread(self._path+'default.jpg')
            self.pics.append(img)
        return self.pics
    def perTrans(self,img,points):
        dst = np.float32([[0,0],[0,149],[149,0],[149,149]])
        src = np.float32(points)
        MLft = cv2.getPerspectiveTransform(src[0:4],dst)
        MRit = cv2.getPerspectiveTransform(src[2:],dst)
        Lft = cv2.warpPerspective(img,MLft,(150,150))
        Rit = cv2.warpPerspective(img,MRit,(150,150))
        ROI = np.zeros((150,300,3),np.uint8)
        ROI[0:,0:150]=Lft
        ROI[0:,150:] =Rit
        return ROI
    def connectROI(self):
        self.ROIS = np.zeros((450,300,3),np.uint8)
        for i in range(3):
            key = str(self._group)+'_'+str(i)+'.jpg'
            points = self.label_dic[key]
            ROI = self.perTrans(self.pics[i],points)
            self.ROIS[150*i:150*(i+1),0:] = ROI
        return self.ROIS
    def update(self,group):
        self.readPics(group)
        self.connectROI()
        return self.ROIS
def drawPoints(points,img):
    img=img.copy()
    for point in points:
        cv2.circle(img,point,2,(0,233,0),2)
    return img
cv2.namedWindow("img")

counter = 0 
img_reader=ImgReader(picture_path,label_name)
img = img_reader.update(counter)
counter+=1
while True:
    cv2.imshow('img',img)
    ch=cv2.waitKey(1)
    if ch == 27:   
        break
    if ch == ord('n'):#next
        img=img_reader.update(counter)
        counter+=1
    # if ch == ord('s'):#save points
        # pass
    
        
    

    