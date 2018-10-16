import numpy as np
import cv2

picture_path='./pictures/light/'
label_name='light_label.npy'
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

img_reader=ImgGenerator(picture_path)

writer = LabelRecoder()

while True:
    img=drawPoints(mouse_info.points,img_reader.img)
    cv2.imshow('img',img)
    ch=cv2.waitKey(1)
    if ch == 27:   
        break
    if ch == ord('n'):#next
        if(mouse_info.isReady()):
            writer.insertLabel(img_reader.name,mouse_info.points)
        mouse_info.resetPoints()
        img_reader.update()
    if ch == ord('r'):#reset
        mouse_info.resetPoints()
    # if ch == ord('s'):#save points
    #     if(mouse_info.isReady()):
    #         writer.insertLabel(img_reader.name,mouse_info.points)
    if ch == ord('e'):#end
        writer.saveLabel(label_name)
    if ch == ord('t'):
        test = np.load(label_name)
        print("read %s"%(label_name))
        print(test)
    
        
    

    