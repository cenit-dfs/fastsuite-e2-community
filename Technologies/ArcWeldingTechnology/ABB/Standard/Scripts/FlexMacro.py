# -------------------------------------------------------------------------------------------
# Name: 
# Description: 
# Debugg info: E2@localhost:5254
# Author: 
# Changelog:
#     Version: 1.0
#        Changed by: MPf
#        Date: 09.09.2025
#     
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
from cenpylib import *
from math import *
import sys
import copy
sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "FlexMacro.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."
ERROR_ACTORS_SENSORS = "(Error) Could not find sensors."
ERROR_NUMBER_ACTORS = "(Error) Number actors."

# Operation attribute definition
# KREIS
MEASURE_DIAMETER = "ABBArcSpotDiameter"
# KREUZBOGEN
MEASURE_TOTALANGLE = "ABBArcAngleRange"
MEASURE_ANGLE1 = "ABBArcAngle1"
# GENERAL
MEASURE_ANGLE = "ABBArcSpotWeldAngle"
MEASURE_SPEED = "ABBArcSpotWeldSpeed"
FLIP_UPDOWN = "ABBArcSpotUpDown"
FLIP_180 = "ABBArcSpotSide"
FLIP_INOUT = "ABBArcSpotInOut"
MARKO_VARIANT = "ABBArcSpotVariant"
MARKO_VARIANT_LIST = ["ABBArcSpotKREIS","ABBArcSpotKREUZBOGEN"]
RESOLUTION = "ABBArcSpotNrPoints"
# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   try:
      # get attribute creator
      attribCreator = Operator.GetAttribCreator()
      # get attribute setter
      attribSetter = Operator.GetAttribSetter()
      # get attribute getter
      attribGetter = Operator.GetAttribGetter()
   except:
      logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)

   # attribCreator.AddInt('TestAttributeEvent', 1, 0, 100, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, 'Test parameter')

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# post process attribute
def PostProcessAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

   # YOUR CODE

   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)
    
 
# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   
   # MEASURE_DIAMETER
   measureDiameter = 0.020
   try:
      measureDiameter = abs(attribGetter.GetDouble(MEASURE_DIAMETER))
   except:
      logging.LogError('Cannot get the attribute MEASURE_DIAMETER!')

   # MEASURE_SPEED
   measureSpeed = 0.111
   try:
      measureSpeed = abs(attribGetter.GetDouble(MEASURE_SPEED))
   except:
      logging.LogError('Cannot get the attribute MEASURE_SPEED!')
   
   # MEASURE_ANGLE
   measureAngle =-45.0
   try:
      measureAngle = attribGetter.GetDouble(MEASURE_ANGLE)
   except:
      logging.LogError('Cannot get the attribute MEASURE_ANGLE!')

   # FLIP_UPDOWN
   bFLipUpDown = False
   try:
      bFLipUpDown = abs(attribGetter.GetBool(FLIP_UPDOWN))
   except:
      logging.LogError('Cannot get the attribute FLIP_UPDOWN!')

   # FLIP_180
   bFlip180 = False
   try:
      bFlip180 = abs(attribGetter.GetBool(FLIP_180))
   except:
      logging.LogError('Cannot get the attribute FLIP_180!')

   # FLIP_INOUT
   bFlipInOut = False
   try:
      bFlipInOut = abs(attribGetter.GetBool(FLIP_INOUT))
   except:
      logging.LogError('Cannot get the attribute FLIP_INOUT!')
   
   # VARIANT
   try:
      iVariant = attribGetter.GetEnumIndex(MARKO_VARIANT)
      iVariantName = MARKO_VARIANT_LIST[iVariant]
   except:
      logging.LogError('Cannot get the attribute FLIP_INOUT!')

   # MEASURE_TOTALANGLE
   totalAngle =150.0
   try:
      totalAngle = attribGetter.GetDouble(MEASURE_TOTALANGLE)
   except:
      logging.LogError('Cannot get the attribute MEASURE_TOTALANGLE!')

   # MEASURE_ANGLE1
   Angle1 =30.0
   try:
      Angle1 = attribGetter.GetDouble(MEASURE_ANGLE1)
   except:
      logging.LogError('Cannot get the attribute MEASURE_TOTALANGLE!')

   # RESOLUTION
   iResolution = 7
   try:
      iResolution = attribGetter.GetInteger(RESOLUTION)
   except:
      logging.LogError('Cannot get the attribute RESOLUTION!')

   
   if iVariantName == "KREIS":   
      # Diameter
      d=float(measureDiameter)
      # Weld Angle
      a=-45.0
      # Weld Angle offset 
      b=0.0
      # Ref Point
      ref=Operator.GetRefTpElement()
      ref2=Operator.GetRefToolpathElementPosition()
      ref3=Operator.GetTpElementPosition(ref,POSRELATION_REFERENCEEVENTROOTPOINT)
         # Teach Flags
      tf=ref.GetTeachFlags()
      # Initial
      IM=ref.GetInitialPathMatrix()
      CM=ref.GetMatrix()
      GT=ref.GetGlobalTransformedMatrix()
      # Get reference toolpath element   
      iCircleResolution=iResolution
      parray=[]
      i=0
      while i<iCircleResolution:    
         parray.append(Operator.GetRefTpElement().GetMatrix())
         i+=1
      
      # Set Translation
      i=0
      for p in parray:      
         currentangle=360/(len(parray)-1)*i
         x=d/2*sin(radians(currentangle))
         y=d/2*cos(radians(currentangle))
         p.Translate(x,y,0, True)
         i+=1
         
      #Set Orientation
      i=0
      for p in parray:
         rotangleZ=360/(len(parray)-1)*i
         p.RotateZ(-rotangleZ+b)  
         
         if bFLipUpDown:         
            p.RotateX(-measureAngle+180)
         else:
            p.RotateX(-measureAngle)         
         if bFlip180:
            p.RotateZ(-90)
         else:
            p.RotateZ(90)
         if bFlipInOut:
            p.RotateZ(180)  
         i+=1
      
      # Create Positions
      TParray=[]  
      i=0
      while i<iCircleResolution:
         if i==0:
            TParray.append(Operator.MovePTP(p))
            i+=1
         else:
            TParray.append(Operator.MoveCir(parray[i+1],parray[i]))
            i+=2

      # Create Events
      eventOperator = Operator.GetEventOperator()
      se = eventOperator.AddSpeed(TParray[0], TPINSERTPOS_INSERTBEFORE)
      se.SetPathType(EVENTPATHTYPE_CONTOUR)
      se.SetSpeed(measureSpeed)

      accev = eventOperator.AddAccuracyEvent(TParray[0], TPINSERTPOS_INSERTBEFORE)
      accev.SetAccuracy(0.005)
      accev.SetPathType(EVENTPATHTYPE_CONTOUR)

   if iVariantName == "KREUZBOGEN":
      # Diameter
      d=float(measureDiameter)      
      # Ref Point
      ref=Operator.GetRefTpElement()      
      iCircleResolution=iResolution
      parray=[]
      i=0
      while i<iCircleResolution:    
         parray.append(Operator.GetRefTpElement().GetMatrix())
         i+=1
      
      # Set Translation
      i=0
      for p in parray:      
         currentangle=totalAngle/(len(parray)-1)*i+(180-totalAngle)/2
         x=d/2*sin(radians(currentangle))
         y=d/2*cos(radians(currentangle))         
         # Z-Offset Start/Mitte
         zOffset=GetLinearOverride(-2,2,i,len(parray)-1)
         p.Translate(x,y,-zOffset/1000, True)         
         i+=1
         
      #Set Orientation
      i=0
      for p in parray:
          rotangleZ=totalAngle/(len(parray)-1)*i+(180-totalAngle)/2
          # Kreisrotation
          p.RotateZ(-rotangleZ)
           # Unter/Oben
          if bFLipUpDown:         
             p.RotateX(180)             
          # Aussen/Innen
          if bFlipInOut:
             p.RotateY(180)
             p.RotateX(180)
          # Arbeitswinkel
          RotateMatrix(p,90-measureAngle,0,0)
          # Arbeitswinkelüberhöhung Min/Max
          angularOverrideFactor = GetLinearOverride(-1,1,i,len(parray)-1)
          RotateMatrix(p,angularOverrideFactor*Angle1,0,0)
          # Werkzeug Z
          if bFlip180:
             p.RotateZ(90)           
          #    else:s
          #       p.RotateZ(90)
          #if bFlipInOut:
          #    p.RotateZ(180)
          #
          # Arbeitswinkel
          #p.RotateX(measureAngle)   
          i+=1
      
      # Create Positions
      TParray=[]  
      i=0
      # x1= Operator.GetRefTpElement().GetMatrix()
      # x2= Operator.GetRefTpElement().GetMatrix()
      # # Generate First Approach Point
      # tRotation=parray[0].GetRotation()
      # tTranslation= parray[0].GetPosition().GetXYZ()
      # RotateMatrix(x1,tRotation[0],tRotation[1],tRotation[2])
      # RotateMatrix(x2,tRotation[0],tRotation[1],tRotation[2])
      # x1.Translate(tTranslation[0],tTranslation[1],tTranslation[2],False)
      # x2.Translate(tTranslation[0],tTranslation[1],tTranslation[2],False)

           
      # Generate Second Approach Point           
      #x1.Translate(0.0,0.0,0.1,True)
      #x2.Translate(0.0,0.0,0.05,True)
      #Operator.MovePTP(x1)
      #Operator.MoveLin(x2)

      while i<iCircleResolution:
         if i==0:
            
            TParray.append(Operator.MoveLin(parray[i]))
            i+=1
         else:
            #TParray.append(Operator.MoveCir(parray[i+1],parray[i]))
            #i+=2
            TParray.append(Operator.MoveLin(parray[i]))
            i+=1
      

      
      # Create Events
      eventOperator = Operator.GetEventOperator()
      se = eventOperator.AddSpeed(TParray[0], TPINSERTPOS_INSERTBEFORE)
      se.SetPathType(EVENTPATHTYPE_CONTOUR)
      se.SetSpeed(measureSpeed)
      #accev = eventOperator.AddAccurac
      accev = eventOperator.AddAccuracyEvent(TParray[0], TPINSERTPOS_INSERTBEFORE)
      accev.SetAccuracy(0.005)
      accev.SetPathType(EVENTPATHTYPE_CONTOUR)

def RotateMatrix(mat,A,B,C):
   mat.RotateZ(C)
   mat.RotateY(B)
   mat.RotateX(A)
   return mat

def GetLinearOverride(minvalue, maxvalue, number, count):
   if number < count/2:
      return minvalue + number * (maxvalue-minvalue)/(count/2)
   elif number == count/2:
      return maxvalue
   else:
      return minvalue + (count-number) * (maxvalue-minvalue)/(count/2)


   
# -------------------------------------------------------------------------------------------
# 
def GetEventName():
   return "FlexMacro"
   
def GetEventUuId():
   return "5183D119-9AE9-48F4-B533-615483E2684E"

def GetIconName():
   return "Points"
   
def GetExplodeCycle():
   return 0
   
def GetMultipleCreationIsPossible():
   return 1

def GetCycleReferenceBehavior():
   return CYCLEREFBEHAVIOR_TEACHABLE
#CYCLEREFBEHAVIOR_HIDDEN    = 0
#CYCLEREFBEHAVIOR_TEACHABLE = 1
#CYCLEREFBEHAVIOR_NORMAL    = 2

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY
#CYCLE_EXPLODEALLOWED       = 0
#CYCLE_EXPLODEFORBIDDEN     = 1
#CYCLE_EXPLODEIMMEDIATELY   = 2
   
def GetEventType():
   return OLPEVENT_PROCESS

def GetCycleRotationFlag():
   return CYCLEROTATION_ROTPATHTOOL
def GetCycleTranslationFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTPATHTOOL
def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTPATHTOOL
def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSYES

def IsMachiningCycle():
   return 1

def GetGroupName():
   return "OlpEvent"