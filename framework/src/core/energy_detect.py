

class BaseEnergyDetector(object):
    def __init__(self,*args,**kwargs):
        NotImplemented
    def __call__(*args,**kwargs):
        '''
        description:
        given the some parameters, predict the target. 
        return the point of armor in the original frame (not the cropped one). If there are more than one armor, return the best one.
        
        return: 
        dict:  {"armor": (255.5,255.3), ""}
        '''

    def update(self,*args,**kwargs):
        NotImplemented
        '''
        update the frame or some parameters of the detector.
        '''
    def set_mode(self,*args,**kwargs):
        NotImplemented
        '''
        set the mode of the detector.
        '''
        
    def show(self):
        NotImplemented
        '''
        Show the debug frame.
        '''
    @staticmethod
    def draw_box(frame,points,color = (0,255,255)):
        for i in range(4):
            cv.line(frame,tuple(points[i%4]),tuple(points[(i+1)%4]),color,2)
        return frame
    
    def reset(self):
        NotImplemented
        '''
        reset the parameters of the detector.
        '''
