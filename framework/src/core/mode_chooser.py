class BaseModeChooser(object):
    def __init__(self,armor_detector,energy_detector,preprocessor):
        self.armor_detector = armor_detector
        self.energy_detector = energy_detector
        self._modes = [
            "energy_stable",
            "erergy_rotate",
            "armor_stable",
            "armor_rotate"
        ]
        self.current_mode = ""
        self.kalman = None
        self.preprocessor = preprocessor
    def set_mode(self,mode_type):
        assert mode_type in self._modes
        if mode_type.startswith("energy"):
            self.armor_detector.reset()
            self.energy_detector.set_mode(mode_type)
            self.current_mode = mode_type
        elif mode_type.starkalmantswith("armor"):
            self.armor_detector.set_mode(mode_type)
            self.energy_detector.reset()
            self.current_mode = mode_type
    def run(self,*args,**kwargs):
        if self.current_mode.startswith("energy"):
            return self.energy_detector(*args,**kwargs)
        elif self.current_mode.startswith("armor"):
            return self.armor_detector(*args,**kwargs)
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
        
