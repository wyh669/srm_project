import sys
from utils.yacs.config import CfgNode as CN
import json
import os
class CapConfig(object):
    def __init__(self):
        self._C = CN()

        self._C.CAMERA = CN()
        self._C.CAMERA.CAMERANUM = 1
        self._C.CAMERA.PIXELFORMAT = "PixelType_Gvsp_BayerRG8"
        self._C.CAMERA.ACQUISITIONFRAMERATE = 500.0
        self._C.CAMERA.GAIN = 1.0
        self._C.CAMERA.EXPOSURETIME = 2500.0
        self._C.CAMERA.BLACKLEVEL = 250
        self._C.CAMERA.HEIGHT = 740
        self._C.CAMERA.WIDTH = 1440
        self._C.CAMERA.VIDEO = CN()
        self._C.CAMERA.VIDEO.USEVIDEO = False
        self._C.CAMERA.VIDEO.VIDEOPATH = "./output/video"
        
        self._C.CAMERA.SAVE = CN()
        self._C.CAMERA.SAVE.SAVETOVIDEO = False
        self._C.CAMERA.SAVE.SAVEPATH = "./output/save"
    @property
    def default(self):
        return _C.clone()
    
    def merge_from_file(self,filename):
        self._C.merge_from_file(filename)
        self._C.freeze()
        print(self._C)
        return self._C
class RoboConfig():
    def __init__(self,cfg_file = "./config.cfg"):
        self.cfg_file = cfg_file
        if not os.path.exists(cfg_file):
            self.reset()
            self.dump()
        else:
            self.load()
    def load(self):
        with open(self.cfg_file,"r") as f:
            cfg = f.read()
            if cfg:
                self.cfg = json.loads(cfg)
    def dump(self):
        with open(self.cfg_file,"w") as f:
            f.write(json.dumps(self.cfg))
    def reset(self):
        '''
        You write your own configs here !!!
        This is the default config. If the config from the file doesn't work, we can reset the config from this function.
        '''
        self.cfg = {
            "red_config":{
                "thre":5,
                "ratio_min":1,
                "ratio_max":9,
                "offset_x":150,
                "offset_y":0
            },
            "blue_config":{
                "thre":5,
                "ratio_min":1,
                "ratio_max":9,
                "offset_x":150,
                "offset_y":0
            }

        }
    def getcfg(self):
        return self.cfg
    def setColorConfig(self,mode = "red",color_cfg = None):
        if not color_cfg:
            return None
        self.cfg[mode + "_config"] = color_cfg

if __name__ == "__main__":
    cap_cfg = CapConfig()
    cfg = cap_cfg.merge_from_file("/media/xueaoru/DATA/ubuntu/auto_focus/code_framework/projects/xueaoru/BaseConfig.yaml")
    #print(cfg)
    print(cfg.CAMERA)
