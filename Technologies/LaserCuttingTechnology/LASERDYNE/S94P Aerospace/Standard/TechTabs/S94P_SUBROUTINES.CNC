;-------------------- START - PULSE PIERCE, SUBROUTINE #1  --------------------------------------
M5S1
G5
MV5                               ;SELECT GAS FOR PIERCE
PRV6                              ;SET PRESSURE FOR PIERCE
M51M52XV1M53XV2PKV3               ;SET PIERCE LASER PARAMETERS
G20R                              ;SET PLANE ROTATION
G91                               ;SET INCREMENTAL
G00ZV7                            ;DEFOCUS
M100                              ;SHUTTER OPEN
G4X0.1                            ;DELAY FOR SHUTTER    
M54XV4                            ;PIERCE
G00Z-V7                           ;SET BACK TO FOCUS
G20                               ;CANCEL PLANE ROTATION
G90                               ;SET ABSOLUTE
MV5+1                             ;SHUT OFF PIERCE GAS
M6
;-------------------- END - PULSE PIERCE, SUBROUTINE #1 -----------------------------------------
;-------------------- START - PULSE CUT, SUBROUTINE #2 ------------------------------------------
M5S2
G5
MV14                              ;TURN ON CUT GAS
PRV15                             ;SET PRESSURE FOR CUTTING
IF V5!=V14 G4X2.0                 ;IF PIERCE GAS IS DIFFERENT FROM CUT GAS DELAY TWO SECONDS
G20R                              ;SET PLANE ROTATION
G91                               ;SET INCREMENTAL
G00ZV17                           ;DEFOCUS
G20                               ;CANCEL PLANE ROTATION
G90                               ;SET ABSOLUTE
M51M52XV11M53XV12PKV13            ;SET CUTTING PARAMETERS
M100                              ;SHUTTER OPEN
G4X0.1                            ;DELAY FOR SHUTTER    
M60                               ;BEAM ON
FV16                              ;SET FEED RATE
M6
;-------------------- END - PULSE CUT, SUBROUTINE #2 --------------------------------------------
;-------------------- START - PULSE PIERCE AND CUT, SUBROUTINE #3 -------------------------------
M5S3
G5
MV5                               ;SELECT GAS FOR PIERCE
PRV6                              ;SET PRESSURE FOR PIERCE
M51M52XV1M53XV2PKV3               ;SET PIERCE LASER PARAMETERS
G20R                              ;SET PLANE ROTATION
G91                               ;SET INCREMENTAL
G00ZV7                            ;DEFOCUS
M100                              ;SHUTTER OPEN
G4X0.1                            ;DELAY FOR SHUTTER    
M54XV4                            ;PIERCE
G00Z-V7+V17                       ;DEFOCUS FOR CUT
G20                               ;CANCEL PLANE ROTATION
G90                               ;SET ABSOLUTE
M51M52XV11M53XV12PKV13            ;SET CUTTING PARAMETERS
MV5+1                             ;SHUT OFF PIERCE GAS
MV14                              ;TURN ON CUT GAS
PRV15                             ;SET PRESSURE FOR CUTTING
IF V5!=V14 G4X2.0                 ;IF PIERCE GAS IS DIFFERENT FROM CUT GAS DELAY TWO SECONDS
M60                               ;BEAM ON
FV16                              ;SET FEED RATE
M6
;-------------------- END - PULSE PIERCE AND CUT, SUBROUTINE #3 ---------------------------------
;-------------------- START - CW CUT, SUBROUTINE #4 ---------------------------------------------
M5S4
G5
MV24                              ;TURN ON CUT GAS
PRV25                             ;SET PRESSURE FOR CUTTING
IF V5!=V24 G4X2.0                 ;IF PIERCE GAS IS DIFFERENT FROM CUT GAS DELAY TWO SECONDS
G20R                              ;SET PLANE ROTATION
G91                               ;SET INCREMENTAL
G00ZV27                           ;DEFOCUS
G20                               ;CANCEL PLANE ROTATION
G90                               ;SET ABSOLUTE
M50PV23                           ;SET CUTTING PARAMETERS
M100                              ;SHUTTER OPEN
G4X0.1                            ;DELAY FOR SHUTTER    
M60                               ;BEAM ON
FV26                              ;SET FEED RATE
M6
;-------------------- END - CW CUT, SUBROUTINE #4 -----------------------------------------------
;-------------------- START - PULSE WELD, SUBROUTINE #5 -----------------------------------------
M5S5
G5
MV14                              ;TURN ON WELD GAS
M300                              ;TURN ON AIR KNIFE
PRV15                             ;SET PRESSURE FOR WELDING
G4X5.0                            ;DELAY FOR SHIELD GAS
G20R                              ;SET PLANE ROTATION
G91                               ;SET INCREMENTAL
G00ZV17                           ;DEFOCUS
G20                               ;CANCEL PLANE ROTATION
G90                               ;SET ABSOLUTE
M51M52XV11M53XV12PKV13            ;SET WELDING PARAMETERS
M100                              ;SHUTTER OPEN
G4X0.1                            ;DELAY FOR SHUTTER    
M60                               ;BEAM ON
FV16                              ;SET FEED RATE
M6
;-------------------- END - PULSE WELD, SUBROUTINE #5 -------------------------------------------
;-------------------- START - CW WELD, SUBROUTINE #6 --------------------------------------------
M5S6
G5
MV24                              ;TURN ON WELD GAS
M300                              ;TURN ON AIR KNIFE
PRV25                             ;SET PRESSURE FOR WELDING
G4X5.0                            ;DELAY FOR SHIELD GAS
G20R                              ;SET PLANE ROTATION
G91                               ;SET INCREMENTAL
G00ZV27                           ;DEFOCUS
G20                               ;CANCEL PLANE ROTATION
G90                               ;SET ABSOLUTE
M50PV23                           ;SET WELDING PARAMETERS
M100                              ;SHUTTER OPEN
G4X0.1                            ;DELAY FOR SHUTTER    
M60                               ;BEAM ON
FV26                              ;SET FEED RATE
M6
;-------------------- END - CW WELD, SUBROUTINE #6 ----------------------------------------------
;-------------------- START - PULSE PIERCE AND TREPAN, SUBROUTINE #7 ----------------------------
M5S7
G5
MV5                               ;SELECT GAS FOR PIERCE
PRV6                              ;SET PRESSURE FOR PIERCE
M100                              ;SHUTTER OPEN
G4X0.1                            ;DELAY FOR SHUTTER
M51M52XV1M53XV2PKV3               ;SET PIERCE LASER PARAMETERS
G20R                              ;SET PLANE ROTATION
G91                               ;SET INCREMENTAL
G00ZV7                            ;DEFOCUS    
M54XV4                            ;PIERCE
G00Z-V7+V17                       ;DEFOCUS FOR TREPAN
M51M52XV11M53XV12PKV13            ;SET CUTTING PARAMETERS
MV5+1                             ;SHUT OFF PIERCE GAS
MV14                              ;TURN ON CUT GAS
PRV15                             ;SET PRESSURE FOR CUTTING
IF V5!=V14 G4X2.0                 ;IF PIERCE GAS IS DIFFERENT FROM TREPAN GAS DELAY TWO SECONDS
IF V6!=V15 G4X0.5                 ;IF PIERCE PRESSURE IS DIFFERENT FROM TREPAN PRESSURE DELAY HALF SECOND
M60                               ;BEAM ON
FV16                              ;SET FEED RATE
G01X-V31/2                        ;LEAD IN
G7                                ;CONTINIUOUS MOTION
G02IV31/2 J0 RV33                 ;TREPAN HOLE
G5                                ;EXACT POSITION
M61                               ;BEAM OFF
IF V5!=V14 M101                   ;CLOSE SHUTTER IF REQUIRED FOR GAS CHANGE
IF V5!=V14 G4X0.1                 ;DELAY         IF REQUIRED FOR GAS CHANGE
IF V5!=V14 M301M303M305M307       ;GAS OFF       IF REQUIRED FOR GAS CHANGE
G20                               ;CANCEL PLANE ROTATION
G90                               ;SET ABSOLUTE
M6
;-------------------- END - PULSE PIERCE AND TREPAN, SUBROUTINE #7 ---------------------------------
;-------------------- START - LASER OFF, SUBROUTINE #10 -----------------------------------------
M5S10
G5                                ;EXACT POSITION
M61                               ;BEAM OFF
M101                              ;CLOSE SHUTTER
G4X0.1                            ;DELAY FOR SHUTTER
M301M303M305M307M309              ;GAS OFF
M6
;-------------------- END - LASER OFF, SUBROUTINE #10 ------------------------------------------