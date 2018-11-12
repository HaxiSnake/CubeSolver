import numpy as np
import cv2

from Classes import ImgReader, CubeBase

condition='cube2_light'
picture_path='./pictures/'+condition+'/'
label_name='./labels/'+condition+'_label.npy'
feature_file='./labels/'+condition+'_feature.csv'
roi_path=picture_path+'rois/'

   
def drawPoints(points,img):  
    img=img.copy()
    for point in points:
        cv2.circle(img,point,2,(0,233,0),2)
    return img

def calSoftHist(img_bgr):
    bins={  0:[0,30,60,85,135,175,200,255],
            1:[0,60,80,200,255],
            2:[0,40,60,180,210,255]
            }
    hist=[]
    img = cv2.cvtColor(img_bgr,cv2.COLOR_BGR2HSV)
    PIXNUM = img.shape[0]*img.shape[1]
    for i in range(3):
        im = img[:,:,i]
        for j in range(len(bins[i])-1):
            mask = cv2.inRange(im,bins[i][j],bins[i][j+1])
            mask = mask/255
            hist.append(np.sum(mask))
    hist = np.asarray(hist)/PIXNUM
    return hist

def drawHist(hist):
    shape=[200,320]
    img = np.zeros(shape,np.uint8)
    step = int(shape[1]/len(hist))
    _white=(255,255,255)
    for i,value in enumerate(hist):
        intensity = int(value*shape[0])
        cv2.rectangle(img,(i*step,shape[0]),((i+1)*step,shape[0]-intensity),_white,-1)
    cv2.imshow('hist',img)

cv2.namedWindow("img")

counter = 0
img_reader=ImgReader(picture_path,label_name)
img = img_reader.update(counter)
counter+=1
while True:
    cv2.imshow('img',img)
    print("%d group"%(counter-1))
    key = cv2.waitKey(1)
    if key == 27:   
        break
    if (key == ord('n')):
        img=img_reader.update(counter)
        counter+=1
cv2.destroyAllWindows()

    
        
    

       