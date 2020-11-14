import math
from collections import namedtuple
import numpy as np

class BaseArmor(object):
    ArmorPoint = namedtuple("Armor",["x1","y1","x2","y2","x3","y3","x4","y4","theta"])
    def __init__(self,lights):
        '''
            @description: The init function of class Armor. 
            @param lights: Tuple of 2 lights(the type of each light is a list). 
            @return: None
        '''
        self.armor_point = lights # (x1,y1,x2,y2,x3,y3,x4,y4)
    @property
    def armor_point(self):
        '''
            @description: the reader of the attribute "armor_point"
            @param {type}
            @return: armor_point, it is the instance the class ArmorPoint with attribute "x1","y1","x2","y2","x3","y3","x4","y4"
        '''
        return self._armor_point
    @armor_point.setter
    def armor_point(self,lights):
        '''
            @description: set armor_point value. 
            @param {type} 
            @return: None
        '''
        light1, light2 = lights
        # light [(x,y),(x,y),(x,y),(x,y)]
        if len(light1[0]) != 4 or len(light2[0]) != 4:
            return 
        light1,theta1 = self.point_sort(light1[0]),light1[-1]
        light2,theta2 = self.point_sort(light2[0]),light2[-1]
        if light1[0][0]+light1[1][0]+light1[2][0]+light1[3][0] > light2[0][0]+light2[1][0]+light2[2][0]+light2[3][0]:
            light1,light2 = light2,light1
        
        self._armor_point = self.ArmorPoint(
            x1 = int(light1[0][0]),
            y1 = int(light1[0][1]),
            x2 = int(light2[1][0]),
            y2 = int(light2[1][1]), 
            x3 = int(light2[2][0]),
            y3 = int(light2[2][1]),
            x4 = int(light1[3][0]),
            y4 = int(light1[3][1]),
            theta = (theta1 + theta2) / 2.
            )
        self.area1 = self.RectArea(light1) + 1e-7
        self.area2 = self.RectArea(light2) + 1e-7
    @property
    def armor_point_list(self):
        '''
            @description: return the armor in the type of list(rather than the instance of ArmorPoint). 
            @param {type} 
            @return: 
        '''
        armor = self.armor_point
        return np.array([[armor.x1,armor.y1],[armor.x2,armor.y2],[armor.x3,armor.y3],[armor.x4,armor.y4]],dtype = np.float32)
        
    @property
    def size(self):
        '''
            @description: The width and height of a armor. 
            @param {type} 
            @return: list, for example [5,1].
        '''
        if self.armor_point is None:
            return [-1,-1]
        armor = self.armor_point    
        w1 = math.sqrt((armor.x1 - armor.x2)**2 + (armor.y1 - armor.y2)**2)
        w2 = math.sqrt((armor.x3 - armor.x4)**2 + (armor.y3 - armor.y4)**2)
        h1 = math.sqrt((armor.x1 - armor.x4)**2 + (armor.y1 - armor.y4)**2)
        h2 = math.sqrt((armor.x2 - armor.x3)**2 + (armor.y2 - armor.y3)**2)
        return max(max(w1,w2),0),max(max(h1,h2),0)
        
    @property
    def center_point(self):
        '''
            @description: the center point of the armor.
            @param {type} 
            @return: list, for example [1,2]
        '''
        if self.armor_point is None:
            return -1,-1
        armor = self.armor_point
        return [(armor.x1 + armor.x3) / 2.,(armor.y1 + armor.y3) / 2.]
    @property
    def center_light(self):
        '''
            @description: the center of two lights (belongs to a armor).
            @param {type} 
            @return: tuple. For example ((x1,y1),(x2,y2))
        '''
        if self.armor_point is None:
            return (-1,-1),(-1,-1)
        armor = self.armor_point
        return ((armor.x1 + armor.x4) / 2. ,(armor.y1 + armor.y4) / 2.), ((armor.x2 + armor.x3) / 2. ,(armor.y2 + armor.y3) / 2.)
        
    @property
    def dif_xy(self):
        '''
            @description: the difference(x axis and y axis) of the center of two lights.
            @param {type} 
            @return: tuple, for exmaple (5,10)
        '''
        if self.armor_point is None:
            return -1,-1
        l1,l2 = self.center_light
        dif_x = abs(l1[0] - l2[0])
        dif_y = abs(l1[1] - l2[1])
        return dif_x,dif_y
    @property
    def dif_xy_ratio(self):
        '''
            @description: the difference ratio(x axis and y axis) of the center of two lights.
            @param {type} 
            @return: float, for example 0.5
        '''
        if self.armor_point is None:
            return -1
        dif_x,dif_y = self.dif_xy
        return dif_y/(dif_x + 1e-7)
    @property
    def dif_slope(self):
        '''
            @description: The difference of the slopes between two lights(the armor's two lights).
            @param {type} 
            @return: float, for example 0.5
        '''
        if self.armor_point is None:
            return -10
        armor = self.armor_point
        return (armor.y1 + armor.y4 -armor.y3 -armor.y2) / (armor.x1 + armor.x4 - armor.x3 - armor.x2 + 1e-7)
    @property
    def dif_heights(self):
        '''
            @description: the difference of the heights between two lights.
            @param {type} 
            @return: 函数注释
        '''
        if self.armor_point is None:
            return float("inf")
        armor = self.armor_point
        return abs(abs(armor.y1 - armor.y4)-abs(armor.y2 - armor.y3))
    @property
    def slopes(self):
        '''
            @description: the slopes of two lights.
            @param {type} 
            @return: (float,float)
        '''
        return float("inf")
        #return (self.light1[0][1] + - self.light1[3][1]) / (self.light1[0][0] - self.light1[3][1] + 1e-7) , (armor.y2 - armor.y3) / (armor.x2 - armor.x3 + 1e-7)
    @staticmethod
    def point_sort(points):
        '''
            @description: given the points of a light, return the clockwise point light.
            @param {type} 
            @return: [(x1,y1),(x2,y2),(x3,y3),(x4,y4)], it is clockwise!!!!! @@@###
        '''
        p = sorted(points,key = lambda x:(x[0]+x[1]))
        p1 = p[0]
        p3 = p[-1]

        p2 = p[1] if p[1][0] > p[2][0] else p[2]
        p4 = p[1] if p[1][0] < p[2][0] else p[2]
        return [p1,p2,p3,p4]
    @property
    def light_area(self):
        '''
            @description: the area of two lights.
            @param {type} 
            @return: (float,float)
        '''
        return self.area1,self.area2
    @staticmethod
    def RectArea(points):
        def TriArea(p1,p2,p3):
            a = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            b = math.sqrt((p1[0] - p3[0])**2 + (p1[1] - p3[1])**2)
            c = math.sqrt((p2[0] - p3[0])**2 + (p2[1] - p3[1])**2)
            p = (a+b+c)/2.
            return math.sqrt(p*(p-a)*(p-b)*(p-c))
        return TriArea(points[0],points[1],points[2]) + TriArea(points[0],points[3],points[2])
    @property
    def square(self):
        if self.armor_point is None:
            return False
        if abs(self.armor_point.x1 - self.armor_point.x2) < 5 and abs(self.armor_point.x3 - self.armor_point.x4) > 10:
            return False
        if abs(self.armor_point.x3 - self.armor_point.x4) < 5 and abs(self.armor_point.x1 - self.armor_point.x2) > 10:
            return False
        if abs(self.armor_point.y1 - self.armor_point.y4) < 5 and abs(self.armor_point.y2 - self.armor_point.y3) > 10:
            return False
        if abs(self.armor_point.y2 - self.armor_point.y3) < 5 and abs(self.armor_point.y1 - self.armor_point.y4) > 10:
            return False
        return True
    
if __name__ == "__main__":
    '''
    the test code of the above class.
    '''
    light1 = [(0,0),(4,0),(0,4),(4,4)]
    light2 = [(12,4),(16,4),(12,8),(16,8)]
    
    armor = Armor(lights = [light1,light2])
    print(armor.point_sort(light1))
    print(armor.armor_point) # √
    print(armor.armor_point_list)# √
    print(armor.size)# √
    print(armor.center_point)# √
    print(armor.center_light)# √
    #print(armor.de)
    #print(armor.de_heights)
    #print(armor.de_slope)
    #print(armor.light_area)
    print(light_area)
