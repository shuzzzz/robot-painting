import cv2 as cv
import time
from datetime import timedelta
import sys
sys.path.append("..")
from robot import com
from robot import port
import numpy as np

if port.EN_DV==True:
    import dv_processing as dv

class DVSData:
    def __init__(self):
        self.ts = time.time()
    def toDict(self):
        return self.__dict__
    def importDict(self,**entries):
        self.__dict__.update(entries)

frameTime = time.time()
DVSD = DVSData()

if port.EN_DV==True:
    capture = dv.io.CameraCapture()

    accumulator = dv.Accumulator(capture.getEventResolution())
    accumulator.setMinPotential(0.0)
    accumulator.setMaxPotential(1.0)
    accumulator.setNeutralPotential(0.5)
    accumulator.setEventContribution(0.15)
    accumulator.setDecayFunction(dv.Accumulator.Decay.STEP)
    #accumulator.setDecayFunction(dv.Accumulator.Decay.EXPONENTIAL)
    #accumulator.setDecayParam(1e+2)
    accumulator.setIgnorePolarity(False)
    accumulator.setSynchronousDecay(False)

    slicer = dv.EventStreamSlicer()

SM_S = com.SharedMemory(name=com.namespace["DVS"], value=DVSD.toDict(), client=True)

startTime = time.time()

recording = False

if port.EN_DV==True:
    def slicing_callback(events: dv.EventStore):
        global frameTime
        global recording
        global startTime
        global SM_S
        global DVSD
        accumulator.accept(events)
        frame = accumulator.generateFrame()
        frameTime = time.time()
        if SM_S.getAvailability()==True:
            DVSD.img = frame.image.tolist()
            cv.imwrite("./helper/event.bmp",frame.image)
            DVSD.ts = time.time()
            SM_S.setValue(DVSD.toDict())
        #cv.imshow("Event", frame.image)
        cv.waitKey(2)
    slicer.doEveryTimeInterval(timedelta(milliseconds=125), slicing_callback)

    while capture.isRunning():
        #frame = capture.getNextFrame()
        events = capture.getNextEventBatch()
        #if frame is not None:
        #    cv.imshow("GRAY", frame.image)
        #    img_rgb = frame.image
            #DVSD.Gray = frame.image.tolist()
            #if SM_C.getAvailability()==True:
                #SM_C.setValue(DVSD.toDict())
        #if (frameTime-startTime)>1:
        #    startTime = frameTime
        #    if img_rgb is not None:
        #        cv.imwrite('./data/gray/'+str(frameTime)+'.png', img_rgb)
        if events is not None:
            slicer.accept(events)
        cv.waitKey(2)
else:
    def slicing_callback():
        global frameTime
        global recording
        global startTime
        global SM_S
        frame = np.random.randint(0,255,(180,240),dtype=np.uint8)
        frameTime = time.time()
        if SM_S.getAvailability()==True:
            cv.imwrite("./helper/event.bmp",frame)
            DVSD.ts = time.time()
            SM_S.setValue(DVSD.toDict())
        cv.waitKey(2)

    while True:
        slicing_callback()
        cv.waitKey(125)