import sys
import os
import cv2 as cv
sys.path.append(os.path.abspath("../../src/core"))
from lights import BaseLightFilter

class LightFilter(BaseLightFilter):
    def __init__(self,):
        super(LightFilter,self).__init__()
    def __call__(self,contours,have_old_target = False):
        out_lights = []
        if not len(contours):
            return out_lights
        
        for contour in contours:
            area = cv.contourArea(contour)
            #
            if area < 10: # 
                print("light area:{}".format(area))
                continue
            box = cv.minAreaRect(contour)
            (x,y),(w,h),theta = box
            # theta [-90,0]
            if w>h:
                theta = theta + 90
                w,h = h,w
            if theta > -30 and theta < 30: # 
                
                if h>1e-1 and w>1e-1 and w/h > 0.88: # 
                    print("theta:{}".format(w/h))
                    continue
                points = cv.boxPoints(box=box)
                out_lights.append((points,theta))
            else:
                print("theta:{}".format(theta))
        out_lights.sort(key = lambda x:
            (x[0][0][0] + x[0][1][0] + x[0][2][0] + x[0][3][0]))
        #out_lights.sort(key = lambda x: cv.contourArea(x[0]))
        # x,y sort
        if have_old_target:
            out_lights = out_lights[::-1][:3] 
        return out_lights

        


