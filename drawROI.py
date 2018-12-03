import numpy as np
import cv2

condition='cube1_dark'
picture_path='./pictures/'+condition+'/'
label_name='./labels/'+condition+'_label.npy'
feature_file='./labels/'+condition+'_feature.csv'
roi_path=picture_path+'rois/'

class ImgGenerator():
    def __init__(self,picture_path,group=0):
        self.img=None
        self._path=picture_path
        self._group=group 
        self._id=0 #three images in one group
        self.name=str(self._group)+'_'+str(self._id)+'.jpg'
        self.update()
    def update(self):
        if(self._id==3):
            self._id=0
            self._group+=1
        self.name=str(self._group)+'_'+str(self._id)+'.jpg'
        print("Read picture at %s"%(self._path+self.name))
        self.img = cv2.imread(self._path+self.name)
        if(self.img is None):
            print("Can not find picture at %s"%(self._path+self.name))
            self.img = cv2.imread(self._path+'default.jpg')
        self._id+=1

class MouseInfo():
    def __init__(self):
        self.curPix=[0,0]
        self.keynumber=6
        self.points=[] # 
    def onMouse(self,e, x, y, flags, param):
        if e == cv2.EVENT_MOUSEMOVE:
            # Movement
            self.curPix=[x,y]
        elif e == cv2.EVENT_RBUTTONDOWN:
            pass
        elif e == cv2.EVENT_RBUTTONUP:
            pass
        elif e == cv2.EVENT_LBUTTONDOWN:
            if(len(self.points) == self.keynumber):
                self.points = []
            self.points.append((x,y))
        elif e == cv2.EVENT_LBUTTONUP:
            pass      
    def resetPoints(self):
        self.points=[]
    def isReady(self):
        return len(self.points) == self.keynumber
class LabelRecoder():
    def __init__(self):
        self.label={}
    def insertLabel(self,key,points):
        print("insert %s label"%(key))
        self.label[key]=points
    def saveLabel(self,name):
        print("save label")
        np.save(name,self.label)
def drawPoints(points,img):
    img=img.copy()
    for point in points:
        cv2.circle(img,point,2,(0,233,0),2)
    return img
mouse_info = MouseInfo()
cv2.namedWindow("img")
mouse = lambda e,x,y,f,p: mouse_info.onMouse(e,x,y,f,p)
cv2.setMouseCallback("img",mouse)

img_reader=ImgGenerator(picture_path,group=1)

def perTrans(img,points):
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

while True:
    img=drawPoints(mouse_info.points,img_reader.img)
    cv2.imshow('img',img)
    if mouse_info.isReady():
        roi=perTrans(img,mouse_info.points)
        cv2.imshow('roi',roi)
    ch=cv2.waitKey(1)
    if ch == 27:   
        break
    if ch == ord('n'):#next
        mouse_info.resetPoints()
        img_reader.update()
    if ch == ord('r'):#reset
        mouse_info.resetPoints()

    
        
    

    