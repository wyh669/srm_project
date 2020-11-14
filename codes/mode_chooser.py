import sys
import os
sys.path.append(os.path.abspath("../../src/core"))
from mode_chooser import BaseModeChooser
class ModeChooser(BaseModeChooser):
    def __init__(self,armor_detector,energy_detector,mode):
        self.armor_detector = armor_detector
        self.energy_detector = energy_detector
        self._modes = [
            "energy_red_stable",
            "erergy_blue_stable",
            "energy_red_rotate",
            "erergy_blue_rotate",
            "armor_red_stable",
            "armor_red_rotate",
            "armor_blue_stable",
            "armor_blue_rotate"
        ]
        self.current_mode = mode
    def set_mode(self,mode_type):
        assert mode_type in self._modes
        if mode_type.startswith("energy"):
            self.armor_detector.set_mode("stop")
            self.energy_detector.set_mode(mode_type)
            self.current_mode = mode_type
        elif mode_type.startswith("armor"):
            self.armor_detector.set_mode(mode_type)
            self.energy_detector.set_mode("stop")
            self.current_mode = mode_type
    def run(self,frame,lights,img_list,origin_frame,debug):
        if self.current_mode.startswith("energy"):
            return self.energy_detector(*args,**kwargs)
        elif self.current_mode.startswith("armor"):
            return self.armor_detector(frame,lights,img_list,origin_frame,debug)
    def predict(self,target,roi_height,roi_width):
        target[0] = target[0] - 10
        if self.current_mode.endswith("rotate"):    
            self.kalman.correct(np.array(target))
            target[0] = float(self.kalman.predict()[0])
        target[1] = target[1]  - 100
        target[1] = target[1] - 1000./roi_height
        h = int(2 * roi_height)
        w = int(roi_width)
        if h > 250:
            h = 250
        if w > 250:
            w = 250
        self.preprocessor.update_roi(w,h)
        return center
