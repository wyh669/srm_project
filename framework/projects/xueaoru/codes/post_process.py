import sys
import os
sys.path.append(os.path.abspath("../../src/core"))
from post_process import BasePostProcessor
class PostProcessor(BasePostProcessor):
    def __init__(self,*args,**kwargs):
        NotImplemented
        '''
        Given some configs, init the LightFilter.
        '''
    def __call__(self,frame):
        NotImplemented
        '''
        Given some contours, filter the lights and return the lights as a list.
        For example, the input contours is the output of cv.findContours
        the output is [[(x1,y1),(x2,y2),(x3,y3),(x4,y4)],...],
        You can sort them in your way(x axis or area).
        '''
    def update(self,*args,**kwargs):
        NotImplemented
