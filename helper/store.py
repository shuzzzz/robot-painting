import os
import time
import cv2
from pandas import Series,DataFrame
import pandas as pd
import numpy as np

dataFrameTemp = {'FG':[],
       'distance':[],
       'angle':[],
       'area':[],
       'ForceX':[],
       'ForceY':[],
       'ForceZ':[],
       'TimeStamp':[]}

data_raw = {'FG':0,
       'distance':0,
       'angle':0,
       'area':0,
       'ForceX':0,
       'ForceY':0,
       'ForceZ':0,
       'TimeStamp':0}

dvsNewFrameTimeStamp = time.time()
newStrokeStartTime = time.time()

nowStrokeFolder = ""
eventBuffer = []
def makeDir():
    global nowStrokeFolder
    nowStrokeFolder = "./data/"+str(time.time())
    os.system("mkdir "+nowStrokeFolder)
    os.system("mkdir "+nowStrokeFolder+"/event")
def newStroke():
    global eventBuffer
    global data_raw
    global df
    global dataFrameTemp
    global newStrokeStartTime
    data_raw = {'FG':0,
       'Dis':0,
       'Angle':0,
       'Area':0,
       'ForceX':0,
       'ForceY':0,
       'ForceZ':0,
       'TimeStamp':0}
    eventBuffer = []
    newStrokeStartTime = time.time()
    df = DataFrame(dataFrameTemp)
def saveRainbow(img):
    global nowStrokeFolder
    cv2.imwrite(nowStrokeFolder+"/rainbow.png",img)
def saveCrop(img):
    global nowStrokeFolder
    cv2.imwrite(nowStrokeFolder+"/crop.png",img)
def getEvent(pack):
    global eventBuffer
    global dvsNewFrameTimeStamp
    if pack["ts"]>dvsNewFrameTimeStamp:
        dvsNewFrameTimeStamp = pack["ts"]
        return cv2.imread("./helper/event.bmp")
    else:
        return None
def appendEvent(img):
    eventBuffer.append(img)
def saveEvent(crop):
    global nowStrokeFolder
    global eventBuffer
    for i in range(len(eventBuffer)):
        eventFrame = eventBuffer[i]
        cv2.imwrite(nowStrokeFolder+"/event/"+str(i)+".png",eventFrame)
def fillRaw(data,label):
    global data_raw
    for l in label:
        data_raw[l] = data[l]
def appendRaw():
    global data_raw
    global df
    global newStrokeStartTime
    data_raw['TimeStamp']=time.time()-newStrokeStartTime
    df.loc[len(df)] = data_raw
def saveRaw():
    global nowStrokeFolder
    global df
    df.to_csv(nowStrokeFolder+"/raw.csv")