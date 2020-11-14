import sys
import os
sys.path.append(os.path.abspath("../../src/core"))
from mode_chooser import BaseModeChooser
class ModeChooser(BaseModeChooser):
    def __init__(self,armor_detector,energy_detector,mode):
        self.armor_detector = armor_detector
        self.energy_detector = energy_detector
        self._modes = [
            "armor_stable",
            "armor_rotating",
            "energy_stable",
            "energy_rotating"
        ]
        self.current_mode = mode
    def set_mode(self,mode_type):
        assert mode_type in self._modes
        self.current_mode = mode_type
    def run(self,*args,**kwargs):
        if self.current_mode.startswith("energy"):
            return self.energy_detector(*args,**kwargs)
        elif self.current_mode.startswith("armor"):
            return self.armor_detector(*args,**kwargs)
