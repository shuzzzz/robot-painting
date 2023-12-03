import serial
import time
import sys
import struct
sys.path.append("..")
import numpy as np
from robot import port
from robot import com

if port.SIMULATE==False:
    portx=port.serialPortx
    bps=460800
    timex=0
    ser=serial.Serial(portx,bps,timeout=timex)

class FrameData:
    def __init__(self):
        self.Status = 0 #Refer to table below 16bit bitmask 2
        self.ForceX = 0 #X component of force in N Float 4
        self.ForceY = 0 #Y component of force in N Float 4
        self.ForceZ = 0 #Z component of force in N Float 4
        self.TorqueX = 0 #X component of torque in Nm Float 4
        self.TorqueY = 0 #Y component of torque in Nm Float 4
        self.TorqueZ = 0 #Z component of torque in Nm Float 4
        self.Timestamp = 0 #In microseconds Uint32 4
        self.Temperature = 0 #Temperature of sensor in degrees Celsius Float 4
        self.checksum = 0 #CRC16 X25
    def toDict(self):
        return self.__dict__
    def importDict(self,**entries):
        self.__dict__.update(entries)

def closePort():
    ser.close()

def serialParseOld(FD,buffer):
    cursor=0
    while True:
        byt = buffer[cursor]
        if cursor in [0,1]:
            FD.Status=FD.Status*0x100+byt
        if cursor in [2,3,4,5]:
            FD.ForceX=FD.ForceX*0x100+byt
        if cursor in [6,7,8,9]:
            FD.ForceY=FD.ForceY*0x100+byt
        if cursor in [10,11,12,13]:
            FD.ForceZ=FD.ForceZ*0x100+byt
        if cursor in [14,15,16,17]:
            FD.TorqueX=FD.TorqueX*0x100+byt
        if cursor in [18,19,20,21]:
            FD.TorqueY=FD.TorqueY*0x100+byt
        if cursor in [22,23,24,25]:
            FD.TorqueZ=FD.TorqueZ*0x100+byt
        if cursor in [26,27,28,29]:
            FD.Timestamp=FD.Timestamp*0x100+byt
        if cursor in [30,31,32,33]:
            FD.Temperature=FD.Temperature*0x100+byt
        if cursor in [34,35]:
            FD.checksum=FD.checksum*0x100+byt
        cursor+=1
        if cursor==35:
            if FD.Status==0:
                return [True,FD]
            else:
                return [False,FD]

def serialParse(FD,buffer):
    FD.Status = buffer[0]*0x100+buffer[1]
    FD.ForceX = struct.unpack('f', buffer[2:6])[0]
    FD.ForceY = struct.unpack('f', buffer[6:10])[0]
    FD.ForceZ = struct.unpack('f', buffer[10:14])[0]
    FD.TorqueX = struct.unpack('f', buffer[14:18])[0]
    FD.TorqueY = struct.unpack('f', buffer[18:22])[0]
    FD.TorqueZ = struct.unpack('f', buffer[22:26])[0]
    if FD.Status==0:
        return [True,FD]
    else:
        return [False,FD]

if port.SIMULATE==True:
    def mainLoop():
        empData = FrameData()
        SM = com.SharedMemory(name=com.namespace["FT"], value=empData.toDict(), client=True)
        del empData
        while True:
            time.sleep(0.05)
            FD = FrameData()
            FD.ForceX = np.random.randint(0,10)+10
            FD.ForceY = np.random.randint(0,10)+10
            FD.ForceZ = np.random.randint(0,10)+10
            if SM.getAvailability()==True:
                SM.setValue(FD.toDict())

else:
    def mainLoop():
        empData = FrameData()
        SM = com.SharedMemory(name=com.namespace["FT"], value=empData.toDict(), client=True)
        del empData
        buffer = b''
        while True:
            byt = ser.read()
            if byt==b'':
                continue
            buffer+=(byt)
            if len(buffer) > 40:
                buffer = buffer[1:]
                if(buffer[0:1]==b'\xaa'):
                    FD = FrameData()
                    flag,res = serialParse(FD,buffer[1:])
                    if flag==True:
                        FD.ForceX -= port.X_bias
                        FD.ForceY -= port.Y_bias
                        FD.ForceZ -= port.Z_bias
                        #print(float("{:.2f}".format(FD.ForceX)),float("{:.2f}".format(FD.ForceY)),float("{:.2f}".format(FD.ForceZ)))
                        if port.LOG==True:
                            FG = (FD.ForceX**2 + FD.ForceY**2 + FD.ForceZ**2)**0.5
                            print(float("{:.2f}".format(FG)))
                        if SM.getAvailability()==True:
                            SM.setValue(FD.toDict())
                        #time.sleep(0.1)

mainLoop()