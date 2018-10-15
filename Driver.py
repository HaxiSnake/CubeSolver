import serial
import time
import os

CLOSE_TIME = 0.3
OPEN_TIME  = 0.2
HALF       = 0.2
QUARTER    = 0.2
class Robot:
    def __init__(self,SerialPort):
        self.ser = serial.Serial(SerialPort,baudrate=115200,timeout=1)
        self.order = ""
        self.status = ['F','B','L','R','U','D']
        if self.ser.isOpen() is False:
            print("Can not connect to Robot!")
            exit()
    def CubeRotate(self,hand,angle):
        """ hand  1:Right 0:Left 
            angle 1:90 clocksize, 3:-90 clocksize, 2:180"""
        if(hand==1):
            thisHand = 'a'
            otherHand = 'b'
        else:
            thisHand = 'b'
            otherHand = 'a'
        if (angle==3):
            self.order = self.order + otherHand + 'o' + ':' + thisHand + '-' + ':'
            self.order = self.order + otherHand + 'c' + ':' + thisHand + 'o' + ':'
            self.order = self.order + thisHand + '+' + ':' + thisHand + 'c' + ':'
            if(hand==1):
                s = self.status
                temp = [s[4],s[5],s[2],s[3],s[1],s[0]]
                self.status = temp
            else:
                s = self.status
                temp = [s[0],s[1],s[5],s[4],s[2],s[3]]
                self.status = temp
        elif (angle==1):
            self.order = self.order + otherHand + 'o' + ':' + thisHand + '+' + ':'
            self.order = self.order + otherHand + 'c' + ':' + thisHand + 'o' + ':'
            self.order = self.order + thisHand + '-' + ':' + thisHand + 'c' + ':'
            if(hand==1):
                s = self.status
                temp = [s[5],s[4],s[2],s[3],s[0],s[1]]
                self.status = temp
            else:
                s = self.status
                temp = [s[0],s[1],s[4],s[5],s[3],s[2]]
                self.status = temp
        elif (angle==2):
            self.order = self.order + otherHand + 'o' + ':' + thisHand + "++" + ':'
            self.order = self.order + otherHand + 'c' + ':' 
            if(hand==1):
                s = self.status
                temp = [s[1],s[0],s[2],s[3],s[5],s[4]]
                self.status = temp
            else:
                s = self.status
                temp = [s[0],s[1],s[3],s[2],s[5],s[4]]
                self.status = temp
    def FaceRotate(self,hand,angle):
        """ hand  1:Right 0:Left 
            angle 3:90 clocksize, 1:-90 clocksize, 2:180"""
        if(hand==1):
            thisHand = 'a'
            otherHand = 'b'
        else:
            thisHand = 'b'
            otherHand = 'a'
        if (angle==1):
            self.order = self.order + thisHand + "-:" + thisHand + "o:" + thisHand + "+:" + thisHand + "c:"
        elif (angle==3):
            self.order = self.order + thisHand + "+:" + thisHand + "o:" + thisHand + "-:" + thisHand + "c:"
        elif (angle==2):
            self.order = self.order + thisHand + "++:"
    def Trim(self,hand,direction):
        """ hand  1:Right 0:Left 
            direction 1:clocksize, -1:anticlocksize"""
        if(hand==1):
            thisHand = 'a'
            otherHand = 'b'
        else:
            thisHand = 'b'
            otherHand = 'a'
        if(direction==1):
            self.order=self.order+thisHand+"w:"
        elif(direction==-1):
            self.order=self.order+thisHand+'s:'
    def generateOrder(self,solutation):
        for com in solutation:
            face = self.status.index(com[0])
            angle = int(com[1])
            if( face == 0 ):
                self.CubeRotate(1,2)
                self.FaceRotate(0,angle)
            elif ( face == 1 ):
                self.FaceRotate(0,angle)
            elif ( face == 2 ):
                self.CubeRotate(0,2)
                self.FaceRotate(1,angle)
            elif ( face == 3 ):
                self.FaceRotate(1,angle)
            elif ( face == 4 ):
                self.CubeRotate(1,1)
                self.FaceRotate(0,angle)
            elif ( face == 5 ):
                self.CubeRotate(1,3)
                self.FaceRotate(0,angle)
        print("origin order",self.order)
        print("tail order:",self.order[-10:-1])
        if self.order[-10:-1] == "ao:a-:ac:" :
            self.order = self.order[0:-10] + "ao:bo:ac-:ac:"
        elif self.order[-10:-1] == "bo:b-:bc:":
            self.order = self.order[0:-10] + "bo:ao:bc-:bc:"
        elif self.order[-10:-1] == "ao:a+:ac:" :
            self.order = self.order[0:-10] + "ao:bo:ac+:ac:"
        elif self.order[-10:-1] == "bo:b+:bc:":
            self.order = self.order[0:-10] + "bo:ao:bc+:bc:"
        elif (self.order[-4:-1] == "ac:"):
            self.order = self.order + "ao:bo:ao:bo:ac:bc:"
        else:
            self.order = self.order + "bo:ao:ao:bo:ac:bc:"
        print("GenerateOrder Done! %d steps"%(len(solutation)))
        
    def sendOrder(self):
        temp = self.order.replace("ac:ao:","")
        temp = temp.replace("bc:bo:","")
        if len(temp) != len(self.order):
            print("delete some orders:")
            print(self.order)
            print(temp)
            self.order = temp
        count = 0
        timeCounter = 0.0
        for string in self.order.split(':'):
            buff = string + '\r\n'
            if len(buff)>2 :
                self.ser.write(buff.encode())
            #0.25 0.15
            if('c' in buff ):
                time.sleep(CLOSE_TIME)
                timeCounter+=CLOSE_TIME
            elif('o' in buff):
                time.sleep(OPEN_TIME)
                timeCounter+=OPEN_TIME
            elif('++' in buff):
                time.sleep(HALF)
                timeCounter+=HALF
            elif('+' in buff or '-' in buff):
                time.sleep(QUARTER)
                timeCounter+=QUARTER
            else:
                pass
            count = count + 1
        print("Total %d orders,%f seconds"%(count,timeCounter))
        self.order = ""
        return timeCounter
class Solver:
    def __init__(self,exePath):
        self.exePath = exePath
        self.inputStr = ""
    def updateInputStr(self,inputS):
        self.inputStr = self.exePath + ' -f ' + inputS
    def solve(self):
        result = os.popen(self.inputStr)
        astr = result.read()
        alist = astr.split()
        alist = alist[1:]
        list_format = []
        for item in alist:
            if (len(item)<2):
                list_format.append(item+'1')
            elif(item[1]=='\''):
                list_format.append(item[0]+'3')
            else:
                list_format.append(item)
        list_format.reverse()
        return list_format
if __name__ == '__main__':
    # robot = Robot('COM9')
    # robot.CubeRotate(1,1)
    # robot.CubeRotate(0,0)
    # robot.sendOrder()
    # robot.FaceRotate(1,1)
    # robot.sendOrder()
    #cube="RU LF UB DR DL BL UL FU BD RF BR FD LDF LBD FUL RFD UFR RDB UBL RBU"
    #cube="UR UB UL UF DF DR DB DL FR FL BR BL URB UBL ULF UFR DRF DFL DLB DBR"
    #cube="UUUFUUFLLBRRURRURRRUUFFFFFFDRRDDDDDDFDDLLLLLLBBLBBBBBB"
    cube="FFFUUUUUUFFDRRRRRRLLLFFDFFDDDBDDBDDBUBBLLLLLLRRRUBBUBB"
    cubeSolver=Solver(r'a.exe')
    cubeSolver.updateInputStr(cube)
    solutation = cubeSolver.solve()
    print(solutation)
    #robot.generateOrder(solutation)
    #robot.sendOrder()

