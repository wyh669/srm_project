import sys
import os
sys.path.append(os.path.abspath("../../src/core"))
from pre_process import BasePreProcessor
import cv2 as cv
class PreProcessor(BasePreProcessor):
    def __init__(self,color):
        '''
        Given some configs, init the preprocessor.
        '''
        self.color = color
        self.left = 0
        self.top = 0
        self.right = 1440
        self.bottom = 740
        self.roi_width = 0
        self.roi_height = 0
        self.old_center = None
    def __call__(self,frame):
        
        '''
        Given some contours, filter the lights and return the lights as a list.
        For example, the input contours is the output of cv.findContours
        the output is [[(x1,y1),(x2,y2),(x3,y3),(x4,y4)],...],
        You can sort them in your way(x axis or area).
        '''
        
        frame = self.update_frame(frame)
        
        r = frame[:,:,2:]
        b = frame[:,:,:1] 
        if self.color == "red":    
            binary = cv.subtract(r,b)
            ret,binary = cv.threshold(binary,180,255,cv.THRESH_BINARY)
        else:
            binary = cv.subtract(b,r)
            ret,binary = cv.threshold(binary,150,255,cv.THRESH_BINARY)
        element = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        binary = cv.dilate(binary,element,iterations =3)
        _,contours,_ = cv.findContours(binary,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return frame,contours
    def update_frame(self,frame):
        h,w = frame.shape[:2]
        if self.old_center is not None:
            left = max(0,self.old_center[0] - 0.75*self.roi_width)
            right = min(w,self.old_center[0] + 0.75*self.roi_width)
            top = max(0,self.old_center[1] - self.roi_height)
            bottom = min(h,self.old_center[1] + self.roi_height)
            
            self.left = int(left)
            self.top = int(top)     
            self.right = int(right)
            self.bottom = int(bottom) 
            frame = frame[int(top):int(bottom),int(left):int(right)]
            #cv.rectangle(self.show,(self.left,self.top),(int(right),int(bottom)),(0,255,255),2)
        else:
            print("****************lost***************")
        return frame
    def update_roi(self,roi_width,roi_height,center):
        self.roi_width = roi_width
        self.roi_height = roi_height
        if self.old_center is not None:
            self.old_center = [self.left + center[0],self.top + center[1]]
        else:
            self.old_center = center
            
    def reset(self):
        self.roi_width = 0
        self.roi_height = 0
        self.old_center = None
    @staticmethod
    def draw_rect(frame,points):
        left_top,right_bottom = points
        cv.rectangle(frame,left_top,right_bottom,(255,255,255),2)  
        return frame      
    @staticmethod
    def draw_box(frame,points,color = (0,255,255)):
        for i in range(4):
            cv.line(frame,tuple(points[i%4]),tuple(points[(i+1)%4]),color,2)
        return frame
        


