import cv2 as cv
import sys
import os
import math
import numpy as np
import glob

sys.path.append(os.path.abspath("../../src/core"))
from armor_detect import BaseArmorDetector
from utils.time import count_time
from model.network import Network


class ArmorDetector(BaseArmorDetector):
    def __init__(self, *args, **kwargs):
        super(ArmorDetector, self).__init__(*args, **kwargs)
        self.img_list = []
        for d in self.templates:
            img = d["image"]
            bbb = process(img)
            self.img_list.append(bbb)
        if self.debug:  # d
            cv.namedWindow("trackbar")
            cv.createTrackbar("thre", "trackbar", self.cfg["thre"], 360, self.trackbar_change)
            cv.createTrackbar("ratio_min", "trackbar", self.cfg["ratio_min"], 10, self.trackbar_change)
            cv.createTrackbar("ratio_max", "trackbar", self.cfg["ratio_max"], 10, self.trackbar_change)
        self.tf_classifier = None

    # Network(graph_path = "/home/nvidia/Desktop/framework/projects/xueaoru/graph.pb")
    def process(src):
        src = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
        ret, src = cv.threshold(src, 127, 255, cv.THRESH_BINARY)

        return src

    def trackbar_change(self, o):  # when trackbar changes, the configer automatically save the config
        thre = cv.getTrackbarPos("thre", "trackbar")
        ratio_min = cv.getTrackbarPos("ratio_min", "trackbar")
        ratio_max = cv.getTrackbarPos("ratio_max", "trackbar")
        setattr(self, "cfg", {
            "thre": thre,
            "ratio_min": ratio_min,
            "ratio_max": ratio_max
        })
        self.configer.setColorConfig(mode=self.mode, color_cfg=self.cfg)
        self.configer.dump()

    @count_time
    def __call__(self, frame, true_lights,img_list,origin_frame,debug):
        #cv.imshow("dsga",frame)
        def points_sorted(points):
            p = sorted(points, key=lambda x: x[0])
            p1 = p[0] if p[0][1] < p[1][1] else p[1]
            p2 = p[2] if p[2][1] < p[3][1] else p[3]
            p3 = p[1] if p[1][1] > p[0][1] else p[0]
            p4 = p[3] if p[3][1] > p[2][1] else p[2]
            return [p1, p2, p3, p4]

        def distance(p1, p2):
            d = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
            return d

        def size(points):
            w = max(distance(points[0], points[1]), distance(points[2], points[3]))
            h = max(distance(points[0], points[2]), distance(points[1], points[3]))
            return [w, h]
        def process(src):
            src = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
            ret, src = cv.threshold(src, 127, 255, cv.THRESH_BINARY)
            return src

        #files=glob.glob('templates/*.png')
        #img_list=[]
        #for file in files:
            #picture=cv.imread(file)
            #picture = process(picture)
            #img_list.append(picture)
        #print(img_list)


        max_level = -100
        c = 1
        for i in range(0, len(true_lights) - 1):
            for j in range(i + 1, min(i + 4, len(true_lights))):
                points1, theta1 = true_lights[i]
                points2, theta2 = true_lights[j]
                p1 = points_sorted(points1)
                p2 = points_sorted(points2)
                
                if theta2 * theta1 < 0:
                    if debug:
                        print('theta*pass',theta2 * theta1)
                    continue
                if abs(theta1 - theta2) > 10:
                    if debug:
                        print('theta-pass',abs(theta1 - theta2))
                    continue
                
                w1, h1 = size(p1)
                w2, h2 = size(p2)
                W = max(distance(p1[0], p2[1]), distance(p1[2], p2[3]))
                H = max(h1, h2)

                if w1 == 0 or h1 == 0 or w2 == 0 or h2 == 0:
                    continue
                
                if max(h1 / h2, h2 / h1) > 1.5:
                    if debug:
                        print('h1/h2 pass',max(h1 / h2, h2 / h1))
                    continue
                
                if W / H > 5:
                    if debug:
                        print('W/H pass',W / H)
                    continue
                slope1=(p1[1][1]-p1[3][1])/(p1[1][0]-p1[3][0]+1e-07)
                slope2=(p2[0][1]-p2[2][1])/(p2[0][0]-p2[2][0]+1e-07)
                #cv.createTrackbar('extend_ratio','trackbar',1,15,lambda x:None)
                #extend_ratio = cv.getTrackbarPos("extend_ratio", "trackbar")
                extend_ratio=1.5
                extend_h=extend_ratio*H
                if debug:
                    print('extend value',extend_h)
                approx=np.array([[p1[1][0]+extend_h/slope1,p1[1][1]+extend_h],[p2[0][0]+extend_h/slope2,p2[0][1]+extend_h],[p1[3][0]-extend_h/slope1,p1[3][1]-extend_h],[p2[2][0]-extend_h/slope2,p2[2][1]-extend_h]],dtype='float32')
                dst=np.array([[0,40],[30,40],[0,0],[30,0]],dtype='float32')
                M=cv.getPerspectiveTransform(approx,dst)
                warped=cv.warpPerspective(frame,M,(30,40))
                warped=cv.cvtColor(warped,cv.COLOR_BGR2GRAY)
                ret,warped=cv.threshold(warped,0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY)
                rotated_show=cv.resize(warped,(300,400))
                #cv.imshow('rotated',rotated_show)
                white = np.sum(warped > 0)
                ratio = white / (30*40)

                list = []
                for img in img_list:
                    match_values = cv.matchTemplate(img, warped, cv.TM_CCOEFF_NORMED)
                    match_value = match_values[0][0]
                    list.append(match_value)
                    if match_value > 0.6:
                        break
                    
                level = max(list)
                    
                if level < 0.6:
                    if debug:
                        print('wrong level:',level)
                        wrong_f = cv.resize(warped, (300, 400))
                        cv.imshow('wrong', wrong_f)
                        print('this is a wrong figure')
                        
                #if ratio < 0.10 or ratio > 0.60:
                    #print('ratio pass',ratio)
                    #continue

                if level > 0.6:
                    if debug:
                        print("figure pass")
                        right_f = cv.resize(warped, (300, 400))
                        cv.imshow('pass', right_f)
                        center_x = int((p1[0][0] + p2[3][0]) / 2)
                        center_y = int((p1[0][1] + p2[3][1]) / 2)
                        center = [center_x, center_y]
                        cv.putText(origin_frame,str(level),(center[0],center[1]),cv.FONT_HERSHEY_DUPLEX,0.6,(255,255,255))
                        #cv.imshow('debug',origin_frame)
                        cv.imwrite('4_3.png',warped)
                    #center_x = int((p1[0][0] + p2[3][0]) / 2)
                    #center_y = int((p1[0][1] + p2[3][1]) / 2)
                    #center = [center_x, center_y]
                    #return (center, H, W)
                
                light_center1 = ((p1[0][0] + p1[3][0]) / 2, (p1[0][1] + p1[3][1]) / 2)
                light_center2 = ((p2[0][0] + p2[3][0]) / 2, (p2[0][1] + p2[3][1]) / 2)
                de_x = abs(light_center1[0] - light_center2[0])
                de_y = abs(light_center1[1] - light_center2[1])
                center_distance = distance(light_center1, light_center2)
                if de_x == 0:
                    if debug:
                        print('de_x=0')
                    continue
                # print(de_y)
                
                if de_y > 100:
                    if debug:
                        print('dey pass',de_y)
                    continue
                
                if de_y / de_x > 0.7:
                    if debug:
                        print('dey/dex pass',de_y / de_x)
                    continue
                
                if level > max_level:
                    max_level=level
                    true_lights1, theta1 = true_lights[i]
                    true_lights2, theta2 = true_lights[j]
                    c = 0

        if c == 0:
            points1 = true_lights1
            points2 = true_lights2
            p1 = points_sorted(points1)
            p2 = points_sorted(points2)
            center_x = int((p1[0][0] + p2[3][0]) / 2)
            center_y = int((p1[0][1] + p2[3][1]) / 2)
            center = [center_x, center_y]
            w1, h1 = size(p1)
            w2, h2 = size(p2)
            W = max(distance(p1[0], p2[1]), distance(p1[2], p2[3]))
            H = max(h1, h2)
            h_ratio=max(h1 / h2, h2 / h1)
            if debug:
                cv.putText(origin_frame,str(h_ratio),(center[0]+50,center[1]+50),cv.FONT_HERSHEY_DUPLEX,0.6,(255,255,255))
                cv.putText(origin_frame,str(W/H),(center[0]+100,center[1]+100),cv.FONT_HERSHEY_DUPLEX,0.6,(255,255,255))
                
                cv.imshow('debug',origin_frame)
            return (center, H, W)
        if c == 1:
            return (None, None, None)




