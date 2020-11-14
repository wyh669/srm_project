# -- coding: utf-8 --
import sys
import copy
import cv2 as cv
from ctypes import *
import os
sys.path.append(os.path.abspath("/opt/MVS/Samples/aarch64/Python"))
sys.path.append(os.path.abspath("/opt/MVS/Samples/aarch64/Python/MvImport"))
import numpy as np
import random
from MvImport.MvCameraControl_class import *
class CapManager():
    def __init__(self,cfg = None,camera_number = 0,debug = False):
        self.debug = debug
        self.camera_cfg = cfg.CAMERA
        self.record = self.camera_cfg.SAVE.SAVETOVIDEO
        if self.camera_cfg.VIDEO.USEVIDEO == False:
            SDKVersion = MvCamera.MV_CC_GetSDKVersion()
            deviceList = MV_CC_DEVICE_INFO_LIST()
            tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
            ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
            if ret != 0:
                print ("enum devices fail! ret[0x%x]" % ret)
                sys.exit()
            if deviceList.nDeviceNum == 0:
                print ("find no device!")
                sys.exit()
            mvcc_dev_info = cast(deviceList.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print ("user serial number: %s" % strSerialNumber)

            self.cam = MvCamera()
            
            stDeviceList = cast(deviceList.pDeviceInfo[int(camera_number)], POINTER(MV_CC_DEVICE_INFO)).contents

            ret = self.cam.MV_CC_CreateHandle(stDeviceList)
            if ret != 0:
                print ("create handle fail! ret[0x%x]" % ret)
                sys.exit()

            ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != 0:
                print ("open device fail! ret[0x%x]" % ret)
                sys.exit()

            ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print ("set trigger mode fail! ret[0x%x]" % ret)
                sys.exit()
            
            ret = self.cam.MV_CC_SetEnumValue("PixelFormat", 0x01080009)
            if ret != 0:
                print ("set pixel type fail! ret[0x%x]" % ret)
                sys.exit()

            ret = self.cam.MV_CC_SetFloatValue("AcquisitionFrameRate", 500.0)
            if ret != 0:
                print ("set frame rete fail! ret[0x%x]" % ret)
                sys.exit()

            ret = self.cam.MV_CC_SetFloatValue("Gain", self.camera_cfg.GAIN)
            if ret != 0:
                print ("set GAIN fail! ret[0x%x]" % ret)
                sys.exit()
            ret = self.cam.MV_CC_SetFloatValue("ExposureTime", self.camera_cfg.EXPOSURETIME)
            if ret != 0:
                print ("set EXPOSURETIME fail! ret[0x%x]" % ret)
                sys.exit()
            ret = self.cam.MV_CC_SetIntValue("BlackLevel", self.camera_cfg.BLACKLEVEL)
            if ret != 0:
                print ("set BLACKLEVEL fail! ret[0x%x]" % ret)
                sys.exit()
            ret = self.cam.MV_CC_SetIntValue("Height", self.camera_cfg.HEIGHT)
            if ret != 0:
                print ("set HEIGHTMAX fail! ret[0x%x]" % ret)
                sys.exit()
            # ch:获取数据包大小 | en:Get payload size
            stParam =  MVCC_INTVALUE()
            memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
            
            ret = self.cam.MV_CC_GetIntValue("PayloadSize", stParam)
            if ret != 0:
                print ("get payload size fail! ret[0x%x]" % ret)
                sys.exit()
            nPayloadSize = stParam.nCurValue

            # ch:开始取流 | en:Start grab image
            ret = self.cam.MV_CC_StartGrabbing()
            if ret != 0:
                print ("start grabbing fail! ret[0x%x]" % ret)
                sys.exit()
            self.nPayloadSize = nPayloadSize
            self.data_buf = (c_ubyte * nPayloadSize)()

        else:
            self.cap = cv.VideoCapture(self.camera_cfg.VIDEO.VIDEO_PATH)
        if self.camera_cfg.SAVE.SAVETOVIDEO:
            self.videoWriter = cv.VideoWriter(self.camera_cfg.SAVE.SAVEPATH + "/" + self.give_me_filename(),cv.VideoWriter_fourcc('X', 'V', 'I', 'D'),30.0,(1440,740),True)
            

    def save_video(self,frame):
        self.videoWriter.write(frame)
    def read(self):
        if self.debug:
            start = cv.getTickCount()
        if self.camera_cfg.VIDEO.USEVIDEO == False:
            stFrameInfo = MV_FRAME_OUT_INFO_EX()
            memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
            ret = self.cam.MV_CC_GetOneFrameTimeout(byref(self.data_buf), self.nPayloadSize, stFrameInfo, 1000)
            
            if ret==0:
                frame = np.array(self.data_buf,dtype = np.uint8).reshape(self.camera_cfg.HEIGHT,self.camera_cfg.WIDTH,1)
                self.frame = cv.cvtColor(frame,cv.COLOR_BayerBG2BGR)
                
                if self.record:
                    self.save_video(self.frame)
                    
                if self.debug:
                    end = cv.getTickCount()
                    print((end - start)/cv.getTickFrequency()*1000,"ms")
    
            
                return True,self.frame
            print("Bug: No frame! What happened ??  Please ask xueaoru.")
            return False,None
        else:
            return self.cap.read()
    def __del__(self):
        try:
            self.release()
        except Exception as e:
            print(e)
            
    def release(self):
        if self.camera_cfg.VIDEO.USEVIDEO == False:
            ret = self.cam.MV_CC_StopGrabbing()
            if ret != 0:
                print ("stop grabbing fail! ret[0x%x]" % ret)
                #del self.data_buf
                sys.exit()

            # ch: | Close device
            ret = self.cam.MV_CC_CloseDevice()
            if ret != 0:
                print ("close deivce fail! ret[0x%x]" % ret)
                #del self.data_buf
                sys.exit()

            # ch: | Destroy handle
            ret = self.cam.MV_CC_DestroyHandle()
            if ret != 0:
                print ("destroy handle fail! ret[0x%x]" % ret)
                #del self.data_buf
                sys.exit()

            #del self.data_buf
        else:
            self.cap.release()
    @staticmethod
    def give_me_filename():
        return "{:6d}.avi".format(random.randint(0,999999))


if __name__ == "__main__":
    cap = CapManager(debug = True)
    while True:
        ret,frame = cap.read()

        if not ret:
            break
        cv.imshow("frame",frame)
        #cv.imshow("frame2",binary2)
        key = cv.waitKey(1)
        if key == ord('q'):
            break
        
        
    cv.destroyAllWindows()
    
