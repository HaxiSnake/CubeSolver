import numpy as np
import cv2
import math
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
    
    def getHsvFeatures(self):
        self.hsv_features=[]
        for img in self.colors:
            feature = self.calHsv(img)
            self.hsv_features.append(feature)
    def calHsv(self,img_bgr):
        """ HSV 三维特征"""
        img = cv2.cvtColor(img_bgr,cv2.COLOR_BGR2HSV)
        hsv_h = cv2.calcHist([img],[0],None,[256],[0,256])
        hsv_s = cv2.calcHist([img],[1],None,[256],[0,256])
        hsv_v = cv2.calcHist([img],[2],None,[256],[0,256])
        h=hsv_h.argmax()
        s=hsv_s.argmax()
        v=hsv_v.argmax()
        hist_item=[h,s,v]
        hist=np.int32(np.around(hist_item))
        return hist

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
        subarray = x1 - x2     
        return np.sum(np.abs(subarray))
    def calDistance_w(self,x1,x2,color='n'):
        '''欧式距离'''
        if color == 'n':
            w = np.asarray([[100, 0, 0],[0, 1, 0],[0, 0, 1]])
        elif color == 'w':
            w = np.asarray([[0, 0, 0],[0, 100, 0],[0, 0, 0]])
        elif color in "bgy":
            w = np.asarray([[100, 0, 0],[0, 1, 0],[0, 0, 1]])
        elif color in "ro":
            w = np.asarray([[0, 0, 0],[0, 45, 0],[0, 0, 15]])
        else:
            w = np.asarray([[100, 0, 0],[0, 1, 0],[0, 0, 1]])
        subarray = x1 - x2
        subarray =  np.dot(subarray,w) 
        return math.sqrt(np.dot(subarray,subarray))    
    def L_one(self,x1,x2):
        """ 一范数 """
        subarray = x1 - x2     
        return np.sum(np.abs(subarray))
    def _KNN(self,target_id,k,fea='soft'):
        if fea=='soft':
            features=self.features
        elif fea=='hsv':
            features=self.hsv_features
        target = features[target_id]
        similarityList=[]
        for i in range(54):
            if self.isUsed[i]:
                continue
            similarityList.append((self.calDistance(target,features[i]),i))
        sim_sorted=sorted(similarityList,key=lambda dis:dis[0])
        ranklist=[]
        for m in range(k):
            ranklist.append(sim_sorted[m][1])
        return ranklist
    def _KNN_W(self,target_id,k,fea='hsv',color='n'):
        if fea=='soft':
            features=self.features
        elif fea=='hsv':
            features=self.hsv_features
        target = features[target_id]
        similarityList=[]
        for i in range(54):
            if self.isUsed[i]:
                continue
            similarityList.append((self.calDistance_w(target,features[i],color),i))
        sim_sorted=sorted(similarityList,key=lambda dis:dis[0])
        ranklist=[]
        for m in range(k):
            ranklist.append(sim_sorted[m][1])
        return ranklist
    def detectSurfaceWithHSV(self):
        """ 魔方识别 """
        white_s = 256
        white_id = 4
        # find white center
        for i in range(6):
            if self.hsv_features[9*i+4][1] < white_s:
                white_s = self.hsv_features[9*i+4][1]
                white_id = 9*i+4
        # find white color
        order=['F','R','L','D','U','B']
        p = (white_id-4)//9
        self.surface[order[p]][0]=white_id
        self.isUsed[white_id]=1
        ranklist=self._KNN_W(white_id,2,'hsv','w')
        for j in range(2):
            self.surface[order[p]][j+1]=ranklist[j]
            self.isUsed[ranklist[j]]=1
        for j in range(2):
            target_id = self.surface[order[p]][j+1]
            ranklist_3 = self._KNN_W(target_id,3,'hsv','w')
            for k in range(3):
                self.surface[order[p]][(j+1)*3+k]=ranklist_3[k]
                self.isUsed[ranklist_3[k]]=1
        for i in range(6):
            if i == p:
                continue
            target_id = 9*i+4
            self.surface[order[i]][0]=target_id
            self.isUsed[target_id]=1
            ranklist=self._KNN_W(target_id,2,'hsv')
            for j in range(2):
                self.surface[order[i]][j+1]=ranklist[j]
                self.isUsed[ranklist[j]]=1
        for i in range(6):
            if i == p:
                continue
            for j in range(2):
                target_id = self.surface[order[i]][j+1]
                ranklist = self._KNN_W(target_id,3,'hsv')
                for k in range(3):
                    self.surface[order[i]][(j+1)*3+k]=ranklist[k]
                    self.isUsed[ranklist[k]]=1
    def detectSurfaceOnline(self,center_label):
        "在线识别魔方，需要知道六个中心面的颜色"
        face=['F','R','L','D','U','B']
        detect_order=[1,5,0,2,4,3]#1:white 5:blue 0:green 2:yellow 4:orange 3:red
        arg={0:'g',1:'w',2:'y',3:'r',4:'o',5:'b'}
        for i in range(6):
            c=detect_order[i]
            f=center_label.index(c)
            self.surface[face[f]][0]=f*9+4
            self.isUsed[9*f+4]=1
        for i in range(6):
            c=detect_order[i]
            f=center_label.index(c)
            target = f*9+4
            ranklist=self._KNN_W(target,8,'hsv',arg[c])
            for j in range(8):
               self.surface[face[f]][j+1]=ranklist[j] 
               self.isUsed[ranklist[j]]=1
        # # 放置中心面
        # for i in range(6):
        #     c=detect_order[i]#按照颜色顺序进行识别
        #     f=center_label.index(c)#找到对应颜色所在面
        #     self.surface[face[f]][0]=f*9+4
        #     self.isUsed[9*f+4]=1
        # # 找最近邻 k=2
        # for i in range(6):
        #     c=detect_order[i]
        #     f=center_label.index(c)
        #     target = f*9+4
        #     ranklist=self._KNN_W(target,2,'hsv',arg[c])
        #     for j in range(2):
        #         self.surface[face[f]][j+1]=ranklist[j]
        #         self.isUsed[ranklist[j]]=1
        # # 找最近邻的最近邻 k=3
        # for i in range(6):
        #     c=detect_order[i]
        #     f=center_label.index(c)
        #     for j in range(2):
        #         target=self.surface[face[f]][j+1]
        #         ranklist=self._KNN_W(target,3,'hsv',arg[c])
        #         for k in range(3):
        #             self.surface[face[f]][(j+1)*3+k]=ranklist[k]
        #             self.isUsed[ranklist[k]]=1



    def detectSurfaceWithGraph(self):
        self.surface={ 'F':[],'B':[],'L':[],'R':[],'U':[],'D':[]}
        knn_graph = []
        order=['F','R','L','D','U','B']
        center_id = [9*i+4 for i in range(6)]
        for i in range(6):
            self.surface[order[i]].append(i*9+4)
            center = self.features[i*9+4]
            for j in range(54):
               if j in center_id:
                   continue
               dist = self.L_one(center,self.features[j])
               knn_graph.append([i,j,dist])
        sim_sorted = sorted(knn_graph,key=lambda dis:dis[2])
        full_face = []
        has_detected_block=[]
        for item in sim_sorted:
            face,block_id,dist = item
            if len(full_face) == 6:
                break
            if face in full_face or block_id in has_detected_block:
                continue
            self.surface[order[face]].append(block_id)
            has_detected_block.append(block_id)
            if len(self.surface[order[face]]) == 9:
                full_face.append(face)  
    def detectSurfaceWithKmeans(self):
        blocks = np.asarray(self.features)
        kmeans = KMeans(n_clusters=6,random_state=10).fit(blocks)
        # print(len(kmeans.labels_))
        # print(kmeans.labels_)
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
        self.getHsvFeatures()
        self.detectSurfaceWithHSV()
        # print(self.surface)
        return self.surface
    def onlineUpdate(self,ROIimg,center_label):
        self.__init__()
        self.ROIS=ROIimg
        self.splitColors()
        self.getHsvFeatures()
        self.detectSurfaceOnline(center_label)
        # print(self.surface)
        return self.surface
    def update(self,ROIimg):
        self.__init__()
        self.ROIS=ROIimg
        self.splitColors()
        self.getFeatures()
        self.detectSurface()
        return self.surface
    def saveFeatures(self,ROIimg,out_file_name,group,ftype="16"):
        self.ROIS=ROIimg
        self.splitColors()
        if ftype=="16":
            self.getFeatures()
            with open(out_file_name,'a+') as out:
                for feature in self.features:
                    line=[str(num) for num in feature]
                    line.append(str(-1))
                    line.append(str(group))
                    line=','.join(line)
                    out.write(line+'\n')
        elif ftype=="hsv":
            self.getHsvFeatures()
            with open(out_file_name,'a+') as out:
                for feature in self.hsv_features:
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
        self.labels={}
        self.cur_labels=[]
        self.readLabels()
        self.result=np.zeros((450,300,3),np.uint8)
    def readLabels(self):
        line=self.color_file.readline()
        while len(line)>1:
            infos=line.rstrip('\n').split(',')
            group=int(infos[-1])
            if(group in self.labels):
                self.labels[group].append(int(infos[-2]))
            else:
                self.labels[group]=[int(infos[-2])]
            line=self.color_file.readline()
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
        for index,key in enumerate(self.cur_labels):
            x1,x2,y1,y2 = self.getRegin(index)
            self.result[y1:y2,x1:x2,:]=colors[key]
        start_pts=[(150,0),(0,150),(0,300)]
        end_pts =[(150,449),(299,150),(299,300)]
        _color=(0,0,0)
        for i in range(3):
            start = start_pts[i]
            end = end_pts[i]
            cv2.line(self.result,start,end,_color,4)
        return self.result
    def getRegin(self,index):
        face = index//9
        pos = index%9
        x1=(face%2)*150 + (pos%3)*50
        x2=x1+50
        y1=(face//2)*150 + (pos//3)*50
        y2=y1+50
        return x1,x2,y1,y2
    def update(self,group):
        self.group=group
        self.cur_labels=self.labels[group]
        img=self.drawLabels()
        return img
    def __del__(self):
        if self.color_file is not None:
            self.color_file.close()
    def readCenter(self,group):
        self.cur_labels=self.labels[group]
        self.group=group
        self.center=[]
        for i in range(6):
            self.center.append(self.cur_labels[9*i+4])
        return self.group, self.center

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
        outgroup=3
        # if(group==outgroup):
        #     print(group,labels)
        #     for i in range(6):
        #         print(labels[i*9:(i+1)*9])
        for key,item in result.items():
            # if(group==outgroup):
            #     print(key)
            #     print(item)
            this_color = labels[center[key]]
            for block in item:
                self.sum+=1
                if labels[block] != this_color:
                    self.confuse.append([group,block,labels[block],this_color])
    def showResult(self,isALL=False):
        color={0:"green ",1:"white ",2:"yellow",3:"red   ",4:"orange",5:"blue  "}
        if isALL is True:
            print("Incorrect Colors")
            print("group\tposition\ttrue_color\tfalse_color")
            for info in self.confuse:
                print("%d\t%d\t\t%s\t\t%s"%(info[0],info[1],color[info[2]],color[info[3]]))
        print("acc is %f %% "%( 100-100*len(self.confuse)/self.sum ))

class CenterReader():
    def __init__(self,center_file):
        try:
            self.center_dic = np.load(center_file)
            self.center_dic = self.center_dic[()]
        except:
            self.center_dic = {}
            print("Can not find center file at %s"%(center_file))
    def getCenter(self,group):
        return self.center_dic[group]