import cv2
import numpy as np
import sys
sys.path.append("..")
from robot import com
from robot import port

class SideCamData:
    def __init__(self):
        self.distance = 0
        self.angle = 0
        self.area = 0
    def toDict(self):
        return self.__dict__
    def importDict(self,**entries):
        self.__dict__.update(entries)

aim_color = port.brush_color

color_dist = {'yellow': {'Lower': np.array([20, 110, 60]), 'Upper': np.array([60, 170, 220])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 0.6255])},
              'green': {'Lower': np.array([35, 43, 35]), 'Upper': np.array([90, 255, 255])},
              }

cap = cv2.VideoCapture(port.sideCamIndex)
cv2.namedWindow('sideCam', 0)
cv2.resizeWindow("sideCam", 640, 480)

def mainLoop():
    SD = SideCamData()
    #SM_S = com.SharedMemory(name=com.namespace["SideCam"]["Adjustment"], client=False)
    SM_C = com.SharedMemory(name=com.namespace["SideCam"]["data"], value=SD.toDict(), client=True)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if frame is not None:
                gs_frame = cv2.GaussianBlur(frame, (5, 5), 0)
                hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)
                erode_hsv = cv2.erode(hsv, None, iterations=2)
                inRange_hsv = cv2.inRange(erode_hsv, color_dist[aim_color]['Lower'], color_dist[aim_color]['Upper'])
                cnts = cv2.findContours(inRange_hsv.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                try:
                    c = max(cnts, key=cv2.contourArea)
                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    boxI = np.int0(box)
                    boxA = boxI[0]-boxI[1]
                    boxA = (boxA[0]**2 + boxA[1]**2)**0.5
                    boxB = boxI[1]-boxI[2]
                    boxB = (boxB[0]**2 + boxB[1]**2)**0.5
                    Area = int(boxA*boxB)
                    if boxA > boxB:
                        Tan = boxI[0]-boxI[1]
                    else:
                        Tan = boxI[1]-boxI[2]
                    if Area > port.minArea:
                        try:
                            Tan = Tan[1]/Tan[0]
                        except:
                            Tan = 999999
                        degree = np.arctan(Tan)/np.pi*180
                        degree = int(0-degree)
                        dis = int((boxI[0]+boxI[1]+boxI[2]+boxI[3])[0]/4)-port.midScreen
                        if port.LOG==True:
                            print("sideCam: ",Area,degree,dis)
                        cv2.putText(frame, "angle "+str(degree), (40,240), cv2.FONT_HERSHEY_COMPLEX, 3, (0,255,255), 5, 4)
                        cv2.putText(frame, "Detect", (40,100), cv2.FONT_HERSHEY_COMPLEX, 3, (0,255,0), 5, 4)
                        cv2.putText(frame, str(dis), (40,360), cv2.FONT_HERSHEY_COMPLEX, 3, (0,255,0), 5, 4)
                        cv2.drawContours(frame, [np.int0(box)], -1, (0, 255, 255), 2)
                        SD.angle = degree
                        SD.area = Area
                        SD.distance = dis
                        if SM_C.getAvailability()==True:
                            SM_C.setValue(SD.toDict())
                    else:
                        cv2.putText(frame, "Not Detect", (40,100), cv2.FONT_HERSHEY_COMPLEX, 3, (255,0,0), 5, 4)
                except:
                    pass
                cv2.imshow('sideCam', frame)
                cv2.waitKey(1)
            else:
                print("error 1")
        else:
            print("error 2")
    cap.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()

mainLoop()