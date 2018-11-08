import numpy as np
import cv2
from sklearn.cluster import KMeans

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
    def L_one(self,x1,x2):
        """ 一范数 """
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
    def detectSurfaceWithGraph(self):
        self.surface={ 'F':[],'B':[],'L':[],'R':[],'U':[],'D':[]}
        knn_graph = []
        order=['F','R','L','D','U','B']
        for i in range(6):
            self.surface[order[i]].append(i*9+4)
            center = self.features[i*9+4]
            for j in range(54):
               if j == i*9+4:
                   continue
               dist = self.L_one(center,self.features[j])
               knn_graph.append([i,j,dist])
        sim_sorted = sorted(knn_graph,key=lambda dis:dis[2])
        full_face = []
        for item in sim_sorted:
            face,block_id,dist = item
            if len(full_face) == 6:
                break
            if face in full_face:
                continue
            self.surface[order[face]].append(block_id)
            if len(self.surface[order[face]]) == 6:
                full_face.append(face)  
    def newDetectSurface(self):
        blocks = np.asarray(self.features)
        kmeans = KMeans(n_clusters=6,random_state=10).fit(blocks)
        print(len(kmeans.labels_))
        print(kmeans.labels_)
        order=['F','R','L','D','U','B']
        labels=kmeans.labels_
        for i in range(6):
            target_id = 9*i+4
            center_color=labels[target_id]
            temp = np.where(labels==center_color)[0]
            self.surface[order[i]]=temp.tolist()
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
    def test(self,ROIimg):
        self.__init__()
        self.ROIS=ROIimg
        self.splitColors()
        self.getFeatures()
        self.detectSurfaceWithGraph()
        print(self.surface)
        return self.surface
    def update(self,ROIimg):
        self.__init__()
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

class ColorReader():
    def __init__(self,color_label_path):
        try:
            self.color_file = open(color_label_path,'r')
        except IOError:
            print("open %s failed!"%(color_label_path))
        self.group=-1
        self.labels=[]
        self.result=np.zeros((450,300,3),np.uint8)
    def readLabels(self):
        self.labels=[]
        self.group+=1
        for i in range(54):
            line=self.color_file.readline()
            line=line.rstrip('\n').split(',')
            if(int(line[-1])==self.group):
                self.labels.append(int(line[-2]))
            else:
                print("Not in the same group!")
    def drawLabels(self):
        colors = {
           -1: (  0,  0,  0), #black
            0: (  0,255,  0), #green
            1: (255,255,255), #white
            2: (  0,255,255), #yellow
            3: (  0,  0,255), #red
            4: (  0, 97,255), #orange
            5: (255,  0,  0)  #blue
            }
        for index,key in enumerate(self.labels):
            x1,x2,y1,y2 = self.getRegin(index)
            self.result[y1:y2,x1:x2,:]=colors[key]
        return self.result
    def getRegin(self,index):
        face = index//9
        pos = index%9
        x1=(face%2)*150 + (pos%3)*50
        x2=x1+50
        y1=(face//2)*150 + (pos//3)*50
        y2=y1+50
        return x1,x2,y1,y2
    def update(self):
        self.readLabels()
        img=self.drawLabels()
        return img
    def __del__(self):
        if self.color_file is not None:
            self.color_file.close()
    

result={'F': [ 4, 3, 5, 20, 18, 26, 44, 48, 50], 
        'B': [49, 7,15, 30, 25,  9, 38, 16, 53], 
        'L': [22, 1, 8, 12, 21, 24, 36, 46, 47], 
        'R': [13,32,10, 17, 51, 52, 27,  2, 19], 
        'U': [40, 0, 6, 28, 29, 34, 37, 42, 43], 
        'D': [31,33,23, 41, 14, 45, 11, 35, 39]}
class ValidateClass():
    def __init__(self):
        self.confuse=[]
        self.sum=0
    def validate(self,group,result,labels):
        if(type(result).__name__!='dict' and type(labels).__name__!='list'):
            print("Wrong input type!")
            exit()
        center={'F':4,'R':13,'L':22,'D':31,'U':40,'B':49}
        if(group==1):
            print(group,labels)
            for i in range(6):
                print(labels[i*9:(i+1)*9])
        for key,item in result.items():
            if(group==1):
                print(key)
                print(item)
            this_color = labels[center[key]]
            for block in item:
                self.sum+=1
                if labels[block] != this_color:
                    self.confuse.append([group,block,labels[block],this_color])
    def showResult(self):
        color={0:"green ",1:"white ",2:"yellow",3:"red   ",4:"orange",5:"blue  "}
        print("Incorrect Colors")
        print("group\tposition\ttrue_color\tfalse_color")
        for info in self.confuse:
            print("%d\t%d\t\t%s\t\t%s"%(info[0],info[1],color[info[2]],color[info[3]]))
        print("acc is %f %% "%( 100-100*len(self.confuse)/self.sum ))

    