import numpy as np
import cv2

class ImgReader():
    def __init__(self,picture_path,label_name,group=0):
        self._path =picture_path
        self._group=group
        self.pics=[]
        self.ROIS = None
        self.colors=[]
        self.features=[]
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

class CubeBase():
    def __init__(self):
        self.surface={
                'F':[-1]*9,
                'B':[-1]*9,
                'L':[-1]*9,
                'R':[-1]*9,
                'U':[-1]*9,
                'D':[-1]*9
            }
        self.colors=[]
        self.features=[]
        self.isUsed=[0]*54
        for i in range(6):
            self.isUsed[9*i+4]=1
        self.ROIS=np.zeros((450,300,3),np.uint8)
        self.result=np.zeros((450,300,3),np.uint8)
    def splitColors(self):
        wid = 150
        hei = 150 
        self.colors=[]
        for i in range(3):
            for j in range(2):
                img = self.ROIS[150*i:150*(i+1),150*j:150*(j+1)]
                for m in range(3):
                    for n in range(3):
                        self.colors.append( img[int(m*wid/3)+15:int((m+1)*wid/3)-15,int(n*hei/3)+15:int((n+1)*hei/3)-15] )
    def getFeatures(self):
        """获取特征"""
        self.features=[]
        for img in self.colors:
            feature = self.calSoftHist(img)
            self.features.append(feature)
        #print(self.features)
    def calSoftHist(self,img_bgr):
        """计算直方图"""
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
                # cv2.imshow(str(j)+'_'+str(i),mask)
        hist = np.asarray(hist)/PIXNUM
        return hist 
    def calDistance(self,x1,x2):
        """ 计算欧式距离 """
        subarray = x1 - x2
        return np.sum(np.abs(subarray))
    def _KNN(self,target_id,k):
        target = self.features[target_id]
        similarityList=[]
        for i in range(54):
            if self.isUsed[i]:
                continue
            similarityList.append((self.calDistance(target,self.features[i]),i))
        sim_sorted=sorted(similarityList,key=lambda dis:dis[0])
        ranklist=[]
        for m in range(k):
            ranklist.append(sim_sorted[m][1])
        return ranklist
    def detectSurface(self):
        """ 魔方识别 """
        order=['F','R','L','D','U','B']
        for i in range(6):
            target_id = 9*i+4
            self.surface[order[i]][0]=target_id
            self.isUsed[target_id]=1
            ranklist=self._KNN(target_id,2)
            for j in range(2):
                self.surface[order[i]][j+1]=ranklist[j]
                self.isUsed[ranklist[j]]=1
        for i in range(6):
            for j in range(2):
                target_id = self.surface[order[i]][j+1]
                ranklist = self._KNN(target_id,3)
                for k in range(3):
                    self.surface[order[i]][(j+1)*3+k]=ranklist[k]
                    self.isUsed[ranklist[k]]=1
    def getRegin(self,index):
        face = index//9
        pos = index%9
        x1=(face%2)*150 + (pos%3)*50
        x2=x1+50
        y1=(face//2)*150 + (pos//3)*50
        y2=y1+50
        return x1,x2,y1,y2
    def drawResult(self):
        colors = {
            'black':(  0,  0,  0),
            'white':(255,255,255),
            'blue':(255,  0,  0),
            'green':(  0,255,  0),
            'yellow':(  0,255,255),
            'orange':(  0, 97,255),
            'red':(  0,  0,255)
        }
        t={
                'F':'green',
                'B':'blue',
                'L':'yellow',
                'R':'white',
                'U':'orange',
                'D':'red'
            }
        for key,block_nums in self.surface.items():
            for index in block_nums:
                x1,x2,y1,y2 = self.getRegin(index)
                self.result[y1:y2,x1:x2,:]=colors[t[key]]
        return self.result
    def update(self,ROIimg):
        self.ROIS=ROIimg
        self.splitColors()
        self.getFeatures()
        self.detectSurface()
        return self.surface
    def saveFeatures(self,ROIimg,out_file_name,group):
        self.ROIS=ROIimg
        self.splitColors()
        self.getFeatures()
        
        with open(out_file_name,'a+') as out:
            for feature in self.features:
                line=[str(num) for num in feature]
                line.append(str(-1))
                line.append(str(group))
                line=','.join(line)
                out.write(line+'\n')
