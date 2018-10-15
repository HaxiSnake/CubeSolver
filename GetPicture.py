#title:GetPicture.py
#author:Dong
#date:20181015
#usage:
#   python GetPicture.py --picture_path=./pictures
#   python GetPicture.py --picture_path=./pictures --serial_port=/dev/ttyUSB0 --camera_id=0
#python_version:3.5
import cv2
import os
import argparse
import Driver

def parse_args():
    '''Get command line arguments'''
    helps='''This script is to get pictures of cube. \n
           To run this script,you need a camera at least. \n
           press s: save one shot for the cube \n
           press t: turn the cube for another face'''
    parser = argparse.ArgumentParser(description=helps)
    parser.add_argument(
        '--picture_path',
        type=str,
        required=True,
        help="path to save pictures")
    parser.add_argument(
        '--sample_start',
        type=int,
        required=False,
        default=0,
        help="the start number for samples")
    parser.add_argument(
        '--serial_port',
        type=str,
        required=False,
        default="",
        help="serial port to robot")
    parser.add_argument(
        '--camera_id',
        type=int,
        required=False,
        default=0,
        help="id for camera")
    return parser.parse_args()

def main():
    '''This script is to get pictures of cube.

        To run this script,you need a camera at least.
        press s: save one shot for the cube.
        press t: turn the cube for another face(only when you have a serial port).'''
    print(main.__doc__)
    args = parse_args()
    cap=cv2.VideoCapture(args.camera_id)
    group_count = args.sample_start
    pic_path = args.picture_path
    pic_count = 0
    robot = None
    if(len(args.serial_port)!=0):
        robot = Driver.Robot(args.serial_port)
    while True:
        ret, img = cap.read()
        ch = cv2.waitKey(1)
        cv2.imshow('img',img)
        if ch==27:
            break
        if ch==ord('s'):
            if(pic_count==3):
                pic_count=0
                group_count+=1
            savename=pic_path+'/'+str(group_count)+'_'+str(pic_count)+'.jpg'
            if not os.path.exists(pic_path):
                os.makedirs(pic_path)
            cv2.imwrite(savename,img)
            print("write %s done!\n"%(savename))
            pic_count+=1
        if ch==ord('t'):
            if(robot is not None):
                robot.CubeRotate(1,1)
                robot.CubeRotate(0,3)
                robot.sendOrder() 
    cv2.destroyAllWindows()
    cap.release()
    exit()
if __name__=="__main__":
    main()

