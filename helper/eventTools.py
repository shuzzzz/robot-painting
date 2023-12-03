import numpy as np
accImg = np.zeros((180,240),dtype=np.uint8)
accMatrix = np.zeros((180,240),dtype=np.int)
def addEvent(event):
    global accMatrix
    global accImg
    accMatrix += event
    