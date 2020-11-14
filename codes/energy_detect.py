
import sys
import os
sys.path.append(os.path.abspath("../../src/core"))
from energy_detect import BaseEnergyDetector
class EnergyDetector(BaseEnergyDetector):
    def __init__(self,*args,**kwargs):
        super(EnergyDetector,self).__init__(*args,**kwargs)

    
    
