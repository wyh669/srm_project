import numpy as np
import cv2 as cv
from numpy.linalg import eig
import glob
import os
import copy
class GradientDescent():
    def __init__(self,T):
        '''
        The gradient descent process.
        '''
        self.T = T #(2,784)
    def __call__(self,x,y):
        r,d = self.T.shape # (2,784)
        a = np.ones(shape = (r,1)) # (2,1)
        t = 0
        while True:
            b = copy.copy(a)
            # (784,2).dot (2,1) -> (784,1) -> (2,1)
            a = a - 0.005 * self.T.dot(x + self.T.T.dot(a) - y)
            t += 1
            #print(a,b)
            if np.sqrt(np.mean((b-a)**2)) < 0.0001 or t > 100:
                break
        return a,self.T


class TanhDistance():
    '''
    given the dataset and x, predict the nearst sample and the distance of them.
    the algorithm make use of the predefined linear transformation.
    '''

    def __init__(self,frame,transforms = None):
        self.vectors = []
        h,w = frame.shape
        self.hw = h*w
        if transforms is not None:
            for transform in transforms:
                t = transform(frame) # (h,w)
                self.vectors.append(np.reshape(t,(h*w,)) - np.reshape(frame,(h*w,)))
        self.gradientDescent = GradientDescent(np.array(self.vectors)) # r,28*28
    def __call__(self,x,y):
        x = np.reshape(x,(self.hw,1))
        y = np.reshape(y,(self.hw,1))
        a,T = self.gradientDescent(x,y) # (28*28,1)
        
        return np.sqrt(np.mean((x + T.T.dot(a) - y)**2)) 
def get_transforms(frame):
    '''
    predefine some linear transformations.
    '''
    h,w = frame.shape
    transformations = []
    # rotate
    delta_theta = 5
    M = cv.getRotationMatrix2D(((w-1)/2.0,(h-1)/2.0),delta_theta,1)
    transformations.append(lambda x:cv.warpAffine(x,M,(w,h)))

    # shift
    delta_x = 2
    delta_y = 0
    M = np.float32([[1,0,delta_x],[0,1,delta_y]])
    transformations.append(lambda x:cv.warpAffine(x,M,(w,h)))
    
    return transformations

class Tan_Feature_extractor():
    def __init__(self,img_path = ""):
        '''
        input: the path of dataset. (the folder rather than the filename)
        '''
        self.files = []
        self.training_M = self.init(img_path) # (n,40,32)
        
    def __call__(self,x): # x -> (32,40)
        assert x.shape[0] == 32 and x.shape[1] == 40
        x = x/255.0
        transforms = get_transforms(x)
        metric = TanhDistance(x,transforms)
        distances = [{"label":filename.split("/")[-1].split("_")[0],"distance":metric(x,y)} for filename,y in zip(self.files,self.training_M)]
        distances.sort(key = lambda x:x["distance"])
        return distances[0]
    def init(self,img_path):
        files = glob.glob("{}/*.jpg".format(img_path))
        self.files = files
        imgs = []
        for file in files:
            img = cv.imread(file,0)
            #img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
            img = cv.resize(img,(32,40))/255.0
            imgs.append(img)
        return imgs

class PCAFeatureExtractor():
    def __init__(self,img_path = ""):
        self.imgW = 32
        self.imgH = 40
        self.files = []
        training_M = self.init(img_path)
        self.M = np.array(training_M).reshape((-1,self.imgW*self.imgH)) # (m,D)
        self.t = self.M - np.mean(self.M,axis = 0) # (m,D)
        C = self.t.dot(self.t.T) # (m,m)
        vals,vecs = eig(C) # 特征值，特征向量 (m,) (m,m)
        indices = np.argsort(vals)
        U = vecs[indices[:-11:-1],:] #(10,m)
        self.U = U.dot(self.t) # (10,D)
        
    def __call__(self,x):
        x = x.reshape((-1,self.imgW*self.imgH)) # (1,D)
        Dx = x - np.mean(self.M,axis = 0) # (1,D)
        return self.U.dot(Dx.T) # (m,1)
    def detect(self,feature):
        df = self.U.dot(self.t.T) - feature #(m,m)
        df = np.sum(np.abs(df),axis = 0)
        #result = np.sqrt(df)/1e5
        result = df
        idx = np.argmin(result)
        score = result[idx]

        number = self.files[idx].split("/")[-1].split("_")[0]
        return number,score
        #print(np.argmin(result))
        #print(result)
    def init(self,img_path):
        files = glob.glob("{}/*.jpg".format(img_path))
        self.files = files
        imgs = []
        for file in files:
            img = cv.imread(file)
            img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
            img = cv.resize(img,(32,40))
            imgs.append(img)
        return imgs