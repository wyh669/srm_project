import sys
import os
import cv2 as cv
import argparse
import copy
sys.path.append(os.path.abspath("../../src"))
from configs.configs import RoboConfig,CapConfig
from device.caps import CapManager
from codes.mode_chooser import ModeChooser
from codes.armor_detect import ArmorDetector
from codes.energy_detect import EnergyDetector
from codes.post_process import PostProcessor
from codes.pre_process import PreProcessor
from codes.lights import LightFilter

parser = argparse.ArgumentParser()
parser.add_argument("-d","--debug",default = False,help="debug mode",action = "store_true")
parser.add_argument("-r","--red",default = False,help="red mode",action = "store_true")
parser.add_argument("-b","--blue",default = False,help="blue mode",action = "store_true")
parser.add_argument("-s","--serial",default = False,help="need serial",action = "store_true")

args = parser.parse_args()
if args.serial:
    from utils.serial import RoboSerial
def keyboard_serial_task(mode_chooser):
    while True:
        word = serial.read()
        if len(word):
            if word[0] == 10:
                mode_chooser.set_mode("armor_stable")
                print("*"*10,"stable")
            elif word[0] == 20:
                mode_chooser.set_mode("armor_rotating")
                print("*"*10,"rotating")
            elif word[0] == 30:
                mode_chooser.set_mode("energy_stable")
                print("*"*10,"stable")
            elif word[0] == 40:
                mode_chooser.set_mode("energy_rotating")
                print("*"*10,"rotating")

if __name__ == "__main__":
    if args.serial:
        serial = RoboSerial()
    else:
        serial = None
    cfg_reader = CapConfig()
    cfg = cfg_reader.merge_from_file("./BaseConfig.yaml")
    robocfg = RoboConfig()
    cap = CapManager(cfg = cfg,camera_number = 0,debug = False)
    
    lightfilter = LightFilter()
    post_processor = PostProcessor()
    if args.red == True:
        armor_detector = ArmorDetector(robocfg, mode = "red",debug = args.debug)#
        energy_detector = EnergyDetector(robocfg,debug = False)#
        mode_chooser = ModeChooser(armor_detector = armor_detector,energy_detector = energy_detector,mode = "armor_stable")
        pre = PreProcessor("red")
    elif args.blue == True:
        armor_detector = ArmorDetector(robocfg, mode = "blue",debug = args.debug)#
        energy_detector = EnergyDetector(robocfg,debug = False)#
        mode_chooser = ModeChooser(armor_detector = armor_detector,energy_detector = energy_detector,mode = "armor_stable")
        pre = PreProcessor("blue")
    if args.serial:
        t1 = threading.Thread(target = keyboard_serial_task,args=(mode_chooser,))
        t1.setDaemon(True) # 
        t1.start()    
    while True:
        ret,frame = cap.read()
        if ret == False:
            break
        roi_frame, contours = pre(frame)
        
        
        if pre.old_center is not None:
            show = pre.draw_rect(copy.copy(frame),[(pre.left,pre.top),(pre.right,pre.bottom)])
        else:
            show = frame
        if args.debug:
            cv.imshow("show",show)
        lights = lightfilter(contours, have_old_target = not(pre.old_center is None))
        result,height,width = mode_chooser.run(roi_frame,lights)
        
        if result is None:
            pre.reset()
        else:
            pre.update_roi(width,height,result)
        target = post_processor(result)      
        key = cv.waitKey(1)
        try:
            if key == ord('s'):
                detector.test("start")
            if key == ord('d'):
                detector.test("end")
            if key == ord('g'):
                configer.dump()
            if key == ord('q'):
                print("quit!")
                del cap  
                break              
            if target is not None:# find it
                if target[0] < 0 or target[0] > 1440 or target[1] <0 or target[1] > 740:
                    if args.serial:    
                        serial.send([720.,200.])
                    else:
                        if args.serial: 
                            serial.send(target)
                else:
                    if args.serial:
                        serial.send([720.,200.])
                
        except KeyboardInterrupt:
            del cap
            print("keyboard ctrl c stop!")
            break        
            
         
