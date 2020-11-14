import cv2 as cv
import numpy as np
from armor import BaseArmor
import copy
import glob
class BaseArmorDetector(object):
    def __init__(self,configer,mode = "red",debug = False):
        self.configer = configer
        self.debug = debug
        self.cfg = configer.getcfg()[mode + "_config"]
        files = glob.glob("./templates/*.jpg")
        self.templates = [{"image":cv.imread(file,0), "label":int(file.split("/")[-1].split("_")[0])} for file in files]
        self.tf_classifier = None
            
    

    def __call__(self,frame,lights):
        '''
        description:
        given the lights(list:[[(x1,y1),(x2,y2),(x3,y3),(x4,y4),theta],...]) and input frame,
        return the point of armor in the original frame (not the cropped one). If there are more than one armor, return the best one.
        
        return: 
        dict:  {"armor": (255.5,255.3), ""}
        '''
        size = frame.shape
        center = None
        final_armor = None 
        height = 0
        width = 0
        max_area =  -float("inf")
        min_score = float("inf")
        if self.debug:
            ratio_min = cv.getTrackbarPos("ratio_min","trackbar") * 0.05
            ratio_max = cv.getTrackbarPos("ratio_max","trackbar") * 0.05
            thre = cv.getTrackbarPos("thre","trackbar")
        else:
            ratio_min = self.cfg["ratio_min"]* 0.05
            ratio_max = self.cfg["ratio_max"]* 0.05
            thre = self.cfg["thre"]
        results = []
        if lights is None or len(lights)< 2:
            return None, None, None
        for i in range(0,len(lights)):
            for j in range(min(len(lights),i+1),min(len(lights),i + 3)):
                light1 = lights[i]
                light2 = lights[j]
                armor = BaseArmor([light1,light2])
                

                # theta 
                theta1,theta2 = lights[i][1],lights[j][1]
                if abs(theta1 - theta2) > 30:
                    if self.debug:
                        print("delta_theta pass:{}".format(abs(theta1 - theta2)))
                    continue    
                if theta1 >10 and theta2 < -10:
                    if self.debug:
                        print("theta pass:{},{}".format(theta1,theta2))
                    continue

                # armor_size
                armor_w,armor_h = armor.size
                if armor_w/armor_h>6:
                    if self.debug:
                        print("amw/wmh pass:{}".format(armor_w/armor_h))
                    continue
                
                # dif_heights
                dif_heights = armor.dif_heights
                if dif_heights>55:
                    if self.debug:
                        print("dif_heights pass:{}".format(dif_heights))
                    continue
                # square or not
                is_square = armor.square
                if not is_square:
                    print("is not square!")
                    continue
                
                # de
                dif_x,dif_y = armor.dif_xy
                if dif_y > 100:
                    if self.debug:
                        print("dif_y pass:{}".format(dif_y))
                    continue
                if dif_y/(dif_x + 1e-7) > 0.5:
                    if self.debug:
                        print("dif pass dif_x:{} dif_y:{}".format(dif_x,dif_y))
                    continue
                # de_ratio
                dif_xy_ratio = armor.dif_xy_ratio
                if dif_xy_ratio > 0.6:
                    if self.debug:
                        print("dif_xy_ratio pass:{}".format(dif_xy_ratio))
                    continue
                
                # roi
                center_x,center_y = armor.center_point
                left = max(0, int(center_x - armor_w * 0.35))
                top = max(0, int(center_y - armor_h * 0.8))
                right = min(size[1], int(center_x + armor_w * 0.35))
                bottom = min(size[0], int(center_y + armor_h * 0.8))
                roi = frame[top:bottom,left:right,:]
                roih,roiw = roi.shape[:2]
                transform = cv.getAffineTransform(np.array([[0,0],[0,roih],[roiw,roih]],dtype = np.float32),np.array([[0,0],[0,40],[32,40]],dtype = np.float32))
                roi = cv.warpAffine(roi,transform,(32,40))
                if roih<5 or roiw < 1:
                    if self.debug:
                        print("roi size pass: {},{}".format(roiw,roih))
                    continue
                
                
                
                gray = cv.cvtColor(roi,cv.COLOR_BGR2GRAY)
                binary = copy.copy(gray)
                #element = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
                #binary = cv.dilate(binary,element,iterations =1)
                #ret,binary = cv.threshold(binary,0,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
                binary[binary > thre] = 255
                binary[binary <= thre] = 0
                
                if self.tf_classifier is not None:
                    #out = self.sess.run(self.output_tensor_name,feed_dict = {self.input_tensor_name:input_test})[0,:]
                    #soft_res = np.exp(out) / np.sum(np.exp(out))
                    out = self.tf_classifier(copy.copy(binary))
                    res = np.argmax(out)
                    if int(res) == 0 and soft_res[0] > 0.6:
                       print("~~~~~~~~~~~classify wrong!!, cls: {}".format(soft_res))
                       continue
                
                # average intensity
                avg_intensity = np.sum(binary>thre)/(binary.shape[0]*binary.shape[1])
                
                
                if roih > 5:
                    c_x,c_y = binary.shape[1]//2,binary.shape[0]//2
                    c_w,c_h = max(binary.shape[1]//5,1),max(binary.shape[0]//5,1)
                    o_b = binary[c_y - c_h:c_y + c_h,c_x - c_w: c_x + c_w]
                    center_intensity = np.sum(o_b>thre)/(o_b.shape[0]*o_b.shape[1])
                    if center_intensity <=0.02:
                        if self.debug:
                            print("center_intensity:{}".format(avg_intensity))
                        continue
                    
                    b_x,b_y = binary.shape[0]//2,binary.shape[1]
                    b_w,b_h = max(binary.shape[0]//5,1),max(binary.shape[1]//5,1)
                    b_b = binary[c_y - c_h:c_y,c_x - c_w: c_x + c_w]
                    bottom_intensity = np.sum(b_b>thre)/(b_b.shape[0]*b_b.shape[1])
                    if bottom_intensity <=0.01:
                        if self.debug:
                            print("bottom_intensity:{}".format(bottom_intensity))
                        continue
                    '''
                    t_x,t_y = binary.shape[0]//2,0
                    t_w,t_h = max(binary.shape[0]//5,1),max(binary.shape[1]//5,1)
                    t_b = binary[0:t_y + t_w,t_x - t_w: t_x + t_w]
                    top_intensity = np.sum(t_b>thre)/(t_b.shape[0]*t_b.shape[1])
                    if top_intensity <=0.01:
                        if self.debug:
                            print("top_intensity:{}".format(top_intensity))
                        continue
                    '''
                #else:
                #    if avg_intensity< ratio_min or avg_intensity > ratio_max:
                #        if self.debug:
                #            print("avg_i:{},roiw:{},roih:{}".format(avg_intensity,roiw,roih))
                #        continue
                score = 0.
                number = 0
                for d in self.templates:
                    template = d["image"]
                    label = d["label"]
                    template = cv.resize(template,(32,32))
                    binary = cv.resize(binary,(32,32))
                    #cv.imshow("binary",binary)
                    res = cv.matchTemplate(binary,template,cv.TM_CCOEFF_NORMED)
                    _,res,_,_ = cv.minMaxLoc(res)
                    if np.sum(res) > score:
                        score = np.sum(res)
                        if score > 0.3:
                            number = label
                if int(number) == 0:
                    print("number 0 pass!")
                    continue
                area_1,area_2 = armor.light_area
                delta_theta = abs(theta1 - theta2)
                results.append((armor,area_1 + area_2,score,delta_theta))
                if area_1 + area_2 > max_area:
                    max_area = area_1 + area_2
            for result in results:
                
                armor,area,score,delta_theta = result

                # weighted light areas and light slopes
                metric = delta_theta#area / max_area + score  #abs(theta1 - theta2)  + (1./area_1 + 1./area_2)*500
                # minimum 
                if metric < min_score:
                    min_score = metric
                    final_armor = armor
                    
                    width, height =  armor.size
                    
                    if self.debug:
                        b = cv.resize(binary,(32*4,40*4))
        
        if final_armor is not None:
            if self.debug:
                #self.draw_box(self.show,[(0,0),(255,0),(255,255),(0,255)])
                points = final_armor.armor_point
                
                key = cv.waitKey(1)
                if key == ord('n'):
                    cv.imwrite("templates/{}.jpg".format(random.randint(0,999999)),b)
                
            center = final_armor.center_point
        else:
            return None,None,None
        if height:
            return center,height,width
        else:
            return None,0,0
        
    def update(self,*args,**kwargs):
        NotImplemented
        '''
        update the frame or some parameters of the detector.
        '''
    def reset(self):
        pass
    
    
    
