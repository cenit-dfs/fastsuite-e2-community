# -------------------------------------------------------------------------------------------
# Name: Create Positions from CLOOS .pkt File 
# Description: 
#
# Author: Markus Pfeifer,Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: Pfeifer
#        Date:       20.03.2025
# -------------------------------------------------------------------------------------------

from centypes import *
import sys
import numpy as np
from tkinter import filedialog
import re
import math


sys.argv= ['']
sys.dont_write_bytecode = True

# globals 
# Number of CLOOS axes to parse (can differ between reality and E2)
gNumberOfAxis=8
gUnusableIncColumns=4

def GetCommandName():
   return "CreateCalibPositions_V1.0_ABB"
   
def GetCommandUuId():
   return "0c6b231b-179f-4376-af6d-f9e80cf6224a"
   
def GetIconName():
   return "COM_ScriptsRun"


# Euler calculation
def euler_to_quaternion(roll, pitch, yaw):
    # Umwandlung von Grad in Radiant
    roll = math.radians(roll)
    pitch = math.radians(pitch)
    yaw = math.radians(yaw)

    # Zwischenwerte berechnen
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    # Quaternion berechnen (ZYX-Reihenfolge)
    q0 = cr * cp * cy + sr * sp * sy  # w
    q1 = sr * cp * cy - cr * sp * sy  # x
    q2 = cr * sp * cy + sr * cp * sy  # y
    q3 = cr * cp * sy - sr * sp * cy  # z

    return (q0, q1, q2, q3)

# Beispiel: 30° Roll, 45° Pitch, 60° Yaw
#quaternion = euler_to_quaternion(30, 45, 60)
#print("ABB Quaternion (q0, q1, q2, q3):", quaternion)


# Beispiel: 30° Roll, 45° Pitch, 60° Yaw
#quaternion = euler_to_quaternion(30, 45, 60)
#print("ABB Quaternion:", quaternion)

# ABB Quaternion calculation
def quaternion_to_euler(q0, q1, q2, q3):
    # Roll (x-Achsen-Drehung)
    sinr_cosp = 2 * (q0 * q1 + q2 * q3)
    cosr_cosp = 1 - 2 * (q1 * q1 + q2 * q2)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-Achsen-Drehung)
    sinp = 2 * (q0 * q2 - q3 * q1)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Verwende 90 Grad, wenn außerhalb des Bereichs
    else:
        pitch = math.asin(sinp)

    # Yaw (z-Achsen-Drehung)
    siny_cosp = 2 * (q0 * q3 + q1 * q2)
    cosy_cosp = 1 - 2 * (q2 * q2 + q3 * q3)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw
# -------------------------------------------------------------------------------------------
# Vektor substraction 
def vec_delta(a, b):
    c = [b[0]-a[0],b[1]-a[1],b[2]-a[2]]
    return c
# -------------------------------------------------------------------------------------------
# Crossproduct 
def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c

# -------------------------------------------------------------------------------------------
    # Center of 3 points
def GetCenterof3Point(P1,P2,P3):
   P1x=P1[0]
   P1y=P1[1]
   P1z=P1[2]
   P2x=P2[0]
   P2y=P2[1]
   P2z=P2[2]
   P3x=P3[0]
   P3y=P3[1]
   P3z=P3[2]

   D21x = P2x-P1x
   D21y = P2y-P1y
   D21z = P2z-P1z
   D31x = P3x-P1x
   D31y = P3y-P1y
   D31z = P3z-P1z

   F2 = 1/2*(D21x*D21x+D21y*D21y+D21z*D21z)
   F3 = 1/2*(D31x*D31x+D31y*D31y+D31z*D31z)

   M23xy = D21x*D31y-D21y*D31x
   M23yz = D21y*D31z-D21z*D31y
   M23xz = D21z*D31x-D21x*D31z

   F23x = F2*D31x-F3*D21x
   F23y = F2*D31y-F3*D21y
   F23z = F2*D31z-F3*D21z

   Fxx=M23xy*M23xy+M23yz*M23yz+M23xz*M23xz

   Cx = P1x+(M23xy*F23y-M23xz*F23z)/(Fxx)
   Cy = P1y+(M23yz*F23z-M23xy*F23x)/(Fxx)
   Cz = P1z+(M23xz*F23x-M23yz*F23y)/(Fxx)
   C=[Cx,Cy,Cz]
   
   return C

def ReadRobotPositionsFile(Operator):
   file_path = filedialog.askopenfilename(title='Select ABB Module file ...',filetypes = (('text files', '*.mod'),('All files', '*.*')))
   return file_path

def ParseRobotPositionsFile(Operator,xfile):
   logging=Operator.GetLoggerOperator()
   logging.LogInfo(str(xfile))

   try:
      with open(xfile, mode="r") as f:
         lines = f.readlines()
   except FileNotFoundError as e:
      logging.LogError(f"File not found: {xfile}")
      return []

   iCounter=0
   Positionlist = []  
   logging.LogInfo(str(gNumberOfAxis))
   for line in lines:      
      if line.startswith("  CONST robtarget"):
         #result=line.replace("  CONST robtarget ","").split(":=")[1].replace(";","")
         # CONST robtarget jPoint2 := [11, 21, 31, 41, 51, 61],[15, 18]
         lhs, rhs = line.split(":=")
         name = lhs.split()[-1]
         rhs = rhs.replace(";", "").strip()
         parts = [p.strip() for p in rhs.split("],")]
         numbers = []
         for p in parts:
            p = p.strip().lstrip("[").rstrip("]")
            nums = [float(v.strip()) for v in p.split(",")]
            numbers.extend(nums)
         result = [name] + numbers
         Positionlist.append(result)
      iCounter+=1
   return Positionlist	

def ModifyActiveProgram(Operator):
   # get loggercccc
   logging=Operator.GetLoggerOperator()
   logging.LogInfo("### Entered Modify ###")
   # Read IncrementConversionValues
   robot=Operator.GetController().GetResources(1, 0)[0]
   # Customizable Values (next version may take them from E2), Problem is that not all axes are defined in E2 (Station 2 axes)
   # The value count must be the same like value count in CLOOS .pkt file (keep in mind that 4 columns don't show values, COlumn 1 is NAME)
   JointStepFactorValues=[9633792,9633792,8904048,4768384,2904436,3351868,999999,15706731,9633792,15706731,9633792]
   JointZeroOffsetValues=[6291456,6291456,6291456,6291456,6291456,6291456,999999,1073741825,1073741825,1073741825,1073741825]

   file=ReadRobotPositionsFile(Operator)
   # Parse File
   posList=ParseRobotPositionsFile(Operator,file)   
   # get active program
   program = Operator.GetActiveProgram()
   # get all operations    
   operations = program.GetOperations()
   # get teach handler
   teachHandler = Operator.GetTeachHandler()
   # get reference position 
   olpPos=teachHandler.GetTpElementPosition(operations[0].GetTpElements()[0],POSRELATION_BASEFRAME)
   # Create TPEs
   for pos in posList:
      newTPE=teachHandler.InsertNewTpElement(olpPos,MOTIONTYPE_LIN,TPINSERTPOS_INSERTAFTER)
      newTPE.SetName(str(pos[0]))
      teachHandler.SetTpElementMotionType(newTPE, MOTIONTYPE_PTP)
      teachHandler.SetTpElementTargetType(newTPE,TARGETTYPE_CARTESIAN)
      nolpPosition=teachHandler.GetTpElementPosition(newTPE, POSRELATION_BASEFRAME)
      logging.LogInfo(str(pos))
      # Robot axis values
      nolpPosition.SetJointValues([pos[1],pos[2],pos[3],pos[4],pos[5],pos[6]])
      # External Axis values (Customizable)
      # nolpPosition.SetExternalJointValues([pos[8],pos[7]])
      teachHandler.ModifyTpElement(nolpPosition)
   iCounter=0
   # Generate Center
   
   return
   