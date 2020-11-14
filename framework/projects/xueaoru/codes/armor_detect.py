import cv2 as cv
import sys
import os
sys.path.append(os.path.abspath("../../src/core"))
from armor_detect import BaseArmorDetector
from utils.time import count_time
from model.network import Network 
class ArmorDetector(BaseArmorDetector):
    def __init__(self,*args,**kwargs):
        super(ArmorDetector,self).__init__(*args,**kwargs)
        if self.debug: # d
            cv.namedWindow("trackbar")
            cv.createTrackbar("thre","trackbar",self.cfg["thre"],360,self.trackbar_change)
            cv.createTrackbar("ratio_min","trackbar",self.cfg["ratio_min"],10,self.trackbar_change)
            cv.createTrackbar("ratio_max","trackbar",self.cfg["ratio_max"],10,self.trackbar_change)
        self.tf_classifier = None#Network(graph_path = "/home/nvidia/Desktop/framework/projects/xueaoru/graph.pb")
    def trackbar_change(self,o):# when trackbar changes, the configer automatically save the config
        thre = cv.getTrackbarPos("thre","trackbar")
        ratio_min = cv.getTrackbarPos("ratio_min","trackbar")
        ratio_max = cv.getTrackbarPos("ratio_max","trackbar")
        setattr(self,"cfg",{
            "thre":thre,
            "ratio_min":ratio_min,
            "ratio_max":ratio_max
        })
        self.configer.setColorConfig(mode = self.mode,color_cfg = self.cfg)
        self.configer.dump()
    @count_time
    def __call__(self,*args,**kwargs):
        return super(ArmorDetector,self).__call__(*args,**kwargs)
