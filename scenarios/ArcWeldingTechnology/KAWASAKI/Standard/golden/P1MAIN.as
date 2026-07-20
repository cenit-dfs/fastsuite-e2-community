.PROGRAM P1MAIN()
;Compensate track/rail/positioner
ROTBASE_ON = 0
CALL P1S1
;Operation Group: GRP001
;Operation: WG1_Seam1
;Compensate track/rail/positioner
ROTBASE_ON = 1
BASE Rot_Base
TOOL P1MAIN_TOOL1
RIGHTY
ABOVE
DWRIST
SPEED 50 ALWAYS
ACCEL 100 ALWAYS
JMOVE #P1MAIN_P0018
CP OFF
JMOVE TRSUB(P1MAIN_P0019)
SET_ARC_W1JOBNO 1 = 1
SETCONDW1 1 = 35,0,0,0,0,0,0,0
LWS TRSUB(P1MAIN_P0020) 
LWC TRSUB(P1MAIN_P0021) ,1
C1WC TRSUB(P1MAIN_P0022) ,1
C2WC TRSUB(P1MAIN_P0023) ,1
LWC TRSUB(P1MAIN_P0024) ,1
C1WC TRSUB(P1MAIN_P0025) ,1
C2WC TRSUB(P1MAIN_P0026) ,1
LWC TRSUB(P1MAIN_P0027) ,1
C1WC TRSUB(P1MAIN_P0028) ,1
C2WC TRSUB(P1MAIN_P0029) ,1
LWC TRSUB(P1MAIN_P0030) ,1
C1WC TRSUB(P1MAIN_P0031) ,1
C2WC TRSUB(P1MAIN_P0032) ,1
LWE TRSUB(P1MAIN_P0033) ,1
SPEED 500 MM/S ALWAYS
ACCURACY 5 ALWAYS
LMOVE TRSUB(P1MAIN_P0034)
CALL P1S2
CALL P1S3
.END
.PROGRAM kr_touch(.&ref,.&offset,.l_rot_base,.search_dist,.search_speed,.frm_ref_id) ; Kawasaki Robotics Touch Sensing
  ; *******************************************************************
  ;
  ; Program:      kr_touch
  ; Comment:      Kawasaki Robotics Touch Sensing
  ; Author:       CENIT AG
  ;
  ; Date:         8/8/2023
  ;
  ; *******************************************************************
  ;
  ;Assign reference points for frame calculation
  CASE INT(.frm_ref_id) OF
  VALUE 1
    POINT FRAME_PT_1 = NULL
    POINT FRAME_PT_2 = NULL
    POINT FRAME_PT_3 = NULL
    POINT FRAME_REF_PT_1 = NULL
    POINT FRAME_REF_PT_2 = NULL
    POINT FRAME_REF_PT_3 = NULL
    POINT FRAME_REF_PT_1 = .ref
  VALUE 2
    POINT FRAME_REF_PT_2 = .ref
  VALUE 3
    POINT FRAME_REF_PT_3 = .ref
  ANY
    PRINT "Frame point index is greater than 3!"
  END
  ;
  if .l_rot_base == 1 THEN
    ; Transform reference point from Rot_Base to B0 since XAC requires B0 coordinates
    POINT .ref_in_b0 = TRSUB (.offset + .ref)
    POINT .ref_in_rb = .offset + .ref
    XAC .ref_in_b0, .touch, .search_dist, .search_speed
    BREAK
    ; Transform touch result from B0 to Rot_Base
    POINT .touch_rb = TRADD (.touch)
    ;remove the TCPs OAT and EXT values from reference and touch positions
    POINT/OAT .ref_in_rb = NULL
    POINT/OAT .touch_rb = NULL
    POINT/EXT .ref_in_rb = NULL
    POINT/EXT .touch_rb = NULL
    ;calculate offset values in rb coordinates
    POINT .offset = .offset + (.touch_rb -.ref_in_rb)
  ELSE
    POINT .ref_in_base = .offset + .ref
    XAC .ref_in_base, .touch, .search_dist, .search_speed
    BREAK
    POINT .ref_in_base_xyz = .ref_in_base
    POINT .touch_xyz = .touch
    POINT/OAT .ref_in_base_xyz = NULL
    POINT/OAT .touch_xyz = NULL
    POINT/EXT .ref_in_rb = NULL
    POINT/EXT .touch_rb = NULL
    POINT .offset = .offset + (.touch_xyz - .ref_in_base_xyz)
  END
.END
.PROGRAM kr_frame(.&ref_pt1,.&ref_pt2,.&ref_pt3,.&frm_pt1,.&frm_pt2,.&frm_pt3,.&offset) ; Kawasaki Robotics Frame Calculation
  ; *******************************************************************
  ;
  ; Program:      kr_frame
  ; Comment:      Kawasaki Robotics Frame Calculation
  ; Author:       CENIT AG
  ;
  ; Date:         9/6/2023
  ;
  ; *******************************************************************
  ;
  ; Define reference frame
  POINT .frm_ref = FRAME (.ref_pt1, .ref_pt2, .ref_pt3, .ref_pt1)
  ; Define corrected reference frame
  POINT .frm_touch = FRAME (.frm_pt1 + .ref_pt1, .frm_pt2 + .ref_pt2, .frm_pt3 + .ref_pt3, .frm_pt1 + .ref_pt1)
  ; Calculate correction and assign to correction ID
  POINT .offset = .frm_touch - .frm_ref
.END
.TRANS
P1MAIN_P0019 200.71 -118 121.71 0 -135 -90 0 180
P1MAIN_P0020 130 -118 51 0 -135 -90 0 180
P1MAIN_P0021 130 -61.21 51 0 -135 -90 0 180
P1MAIN_P0022 130 -55.86 52.07 -20.94 -130.79 -120.36 0 180
P1MAIN_P0023 130 -51.31 55.1 -35.26 -120 -144.74 0 180
P1MAIN_P0024 130 -30.1 76.31 -35.26 -120 -144.74 0 180
P1MAIN_P0025 130 -24.91 79.78 -20.94 -130.79 -120.36 0 180
P1MAIN_P0026 130 -18.79 81 0 -135 -90 0 180
P1MAIN_P0027 130 18.79 81 0 -135 -90 0 180
P1MAIN_P0028 130 24.91 79.78 20.94 -130.79 -59.64 0 180
P1MAIN_P0029 130 30.1 76.31 35.26 -120 -35.26 0 180
P1MAIN_P0030 130 51.31 55.1 35.26 -120 -35.26 0 180
P1MAIN_P0031 130 55.86 52.07 20.94 -130.79 -59.64 0 180
P1MAIN_P0032 130 61.21 51 0 -135 -90 0 180
P1MAIN_P0033 130 118 51 0 -135 -90 0 180
P1MAIN_P0034 200.71 118 121.71 0 -135 -90 0 180
Rot_Base 0 995.4 922.9 0 0 0
.END
.JOINTS
#P1MAIN_P0018 0 -25 -90 0 -75 0 0 180
.END
