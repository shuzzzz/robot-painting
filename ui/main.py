import numpy as np
import pyqtgraph as pg
import time
import sys
sys.path.append("..")
from robot import com
from pyqtgraph.Qt import QtGui, QtCore
from robot.algo import findNewStroke
from robot import port
import cv2 as cv
import os
from robot.helper import store
from robot.helper import align
import copy

cap = cv.VideoCapture(port.highResCamIndex)

recording = False

img_first = None
rgb_frame = None

startTime = time.time()

app = pg.mkQApp("Fractal Example")
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

SM_FT = com.SharedMemory(name=com.namespace["FT"], client=False)
SM_SC = com.SharedMemory(name=com.namespace["SideCam"]["data"], client=False)
SM_DVS = com.SharedMemory(name=com.namespace["DVS"], client=False)

# Set up UI widgets
win = pg.QtWidgets.QWidget()
win.setWindowTitle('paint robot data collection')
layout = pg.QtWidgets.QGridLayout()
win.setLayout(layout)
layout.setContentsMargins(0, 0, 0, 0)

#label = pg.QtWidgets.QLabel('ROI')
#layout.addWidget(label, 0, 0)
#depthSpin = pg.SpinBox(value=5, step=1, bounds=[1, 10], delay=0, int=True)
#depthSpin.resize(100, 20)
#layout.addWidget(depthSpin, 0, 1)

record_button = pg.QtWidgets.QPushButton('Start')
layout.addWidget(record_button, 0, 0)

# Create plot
ftWin = pg.GraphicsLayoutWidget()

p1 = ftWin.addPlot(title="FT-removeG")
curve_FT_final = p1.plot(pen=(200, 200, 200))
p1.setYRange(-10, 10)

p2 = ftWin.addPlot(title="FT-raw")
curve_FT_X = p2.plot(pen=(0, 200, 200))
curve_FT_Y = p2.plot(pen=(200, 0, 200))
curve_FT_Z = p2.plot(pen=(200, 200, 0))
p2.setYRange(-20, 20)

p3 = ftWin.addPlot(title="Brush-Angle")
curve_brushAngle = p3.plot(pen=(0, 200, 200))
p3.setYRange(-90, 90)

layout.addWidget(ftWin, 1, 0)

#line 2
ftWin2 = pg.GraphicsLayoutWidget()

view = ftWin2.addViewBox()
view.setAspectLocked(True)
img_live = pg.ImageItem(border='w')
view.addItem(img_live)

view = ftWin2.addViewBox()
view.setAspectLocked(True)
img_output = pg.ImageItem(border='w')
view.addItem(img_output)

view = ftWin2.addViewBox()
view.setAspectLocked(True)
img_crop = pg.ImageItem(border='w')
view.addItem(img_crop)

layout.addWidget(ftWin2, 2, 0)

#line 3

ftWin3 = pg.GraphicsLayoutWidget()

view2 = ftWin3.addViewBox()
view2.setAspectLocked(True)
event_live = pg.ImageItem(border='w')
view2.addItem(event_live)

#view2 = ftWin3.addViewBox()
#view2.setAspectLocked(True)
#event_acc = pg.ImageItem(border='w')
#view2.addItem(event_acc)
#event_acc.setImage(eventTools.accImg)

layout.addWidget(ftWin3, 3, 0)

exit_button = pg.QtWidgets.QPushButton('Exit')
layout.addWidget(exit_button, 4, 0)

win.show()

def event_click_record():
    global record_button
    global recording
    global img_first
    global img_live
    global img_output
    global img_crop
    if recording==True:
        recording = False
        #end recording
        record_button.setText("Start")
        max_area,output = findNewStroke.parseTwoFrame(img_first,copy.copy(rgb_frame),gray_input=True,visualize=True,filtSmall=True,savePng=False)
        img_output.setImage(output)
        crop = rgb_frame[max_area[1]:max_area[1] + max_area[3],max_area[0]:max_area[0] + max_area[2]]
        #extend = cv.copyMakeBorder(crop, 0, 720-crop.shape[0], 0, 1280-crop.shape[1],cv.BORDER_CONSTANT, value=0)
        img_crop.setImage(np.array(crop))
        store.saveRainbow(output)
        store.saveCrop(np.array(crop))
        store.saveEvent(align.align(max_area))
        store.saveRaw()
        return
    if recording==False:
        recording = True
        #start recording
        record_button.setText("Stop")
        img_first = rgb_frame
        store.makeDir()
        store.newStroke()
        return

def event_click_exit():
    os.system("killall python")

#depthSpin.valueChanged.connect(event_click_record)
record_button.clicked.connect(event_click_record)
exit_button.clicked.connect(event_click_exit)

FGSerial=np.zeros([50])
FXSerial=np.zeros([50])
FYSerial=np.zeros([50])
FZSerial=np.zeros([50])
BASerial=np.zeros([50])

def freshData():
    global FGSerial
    global FXSerial
    global FYSerial
    global FZSerial
    global BASerial
    global data_raw
    global startTime
    global df
    global recording
    global img_live
    global rgb_frame
    global event_live
    time.sleep(0.03)
    if cap.isOpened():
        ret, rgb_frame = cap.read()
        if ret:
            if rgb_frame is not None:
                rgb_frame = cv.cvtColor(rgb_frame,cv.COLOR_RGB2GRAY)
                img_live.setImage(np.array(rgb_frame))
    app.processEvents()
    if SM_FT.getAvailability()==True:
        data = SM_FT.getValue()
        FG = data["ForceZ"]
        store.fillRaw(data,["ForceZ","ForceX","ForceY"])
        #FG = (data["ForceX"]**2 + data["ForceY"]**2 + data["ForceZ"]**2)**0.5
        FGSerial = FGSerial[1:]
        FGSerial = np.append(FGSerial,FG)
        FXSerial = FXSerial[1:]
        FXSerial = np.append(FXSerial,data["ForceX"])
        FYSerial = FYSerial[1:]
        FYSerial = np.append(FYSerial,data["ForceY"])
        FZSerial = FZSerial[1:]
        FZSerial = np.append(FZSerial,data["ForceZ"])
    if SM_SC.getAvailability()==True:
        data = SM_SC.getValue()
        BASerial = BASerial[1:]
        BASerial = np.append(BASerial,data["angle"])
        store.fillRaw(data,["angle","area","distance"])
    curve_FT_final.setData(FGSerial+1.0*BASerial/40.0)
    curve_FT_X.setData(FXSerial)
    curve_FT_Y.setData(FYSerial)
    curve_FT_Z.setData(FZSerial)
    if SM_DVS.getAvailability()==True:
        dvsPack = SM_DVS.getValue()
        event_img = store.getEvent(dvsPack)
        if event_img is not None:
            event_live.setImage(event_img)
    #    data_raw['TimeStamp']=data
    if recording==True:
        store.appendRaw()
        if event_img is not None:
            store.appendEvent(event_img)
    curve_brushAngle.setData(BASerial)
    #if (time.time()-startTime)>10:
    #    startTime = time.time()
    #    df.to_csv("./data/"+str(startTime)+".csv")

timer = QtCore.QTimer()
timer.timeout.connect(freshData)
timer.start(0)

pg.exec()