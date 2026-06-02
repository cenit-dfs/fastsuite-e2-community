.PROGRAM PG02_SE()
;Compensate track/rail/positioner
ROTBASE_ON = 0
;Operation Group: GRP001
POINT PG02_SE_TS_ID_1 = NULL
POINT PG02_SE_TS_ID_2 = NULL
;Operation: WG1_Touch1
BASE NULL
TOOL PG02_SE_TOOL1
RIGHTY
ABOVE
DWRIST
SPEED 200 MM/S ALWAYS
ACCURACY 5 ALWAYS
LMOVE PG02_SE_TS_ID_1 + PG02_SE_P0001
SPEED 15 MM/S ALWAYS
CALL KR_TOUCH (&PG02_SE_P0002, &PG02_SE_TS_ID_1, ROTBASE_ON, 30.0, 15.0, 0)
STABLE 0.1
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_1 + PG02_SE_P0003
;Operation: WG1_Touch2
LMOVE PG02_SE_TS_ID_1 + PG02_SE_P0005
SPEED 15 MM/S ALWAYS
CALL KR_TOUCH (&PG02_SE_P0006, &PG02_SE_TS_ID_1, ROTBASE_ON, 30.0, 15.0, 0)
STABLE 0.1
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_1 + PG02_SE_P0007
SPEED 50 ALWAYS
JMOVE PG02_SE_TS_ID_1 + PG02_SE_P0009
;Operation: WG1_Touch3
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_1 + PG02_SE_P0010
SPEED 15 MM/S ALWAYS
CALL KR_TOUCH (&PG02_SE_P0011, &PG02_SE_TS_ID_1, ROTBASE_ON, 30.0, 15.0, 0)
STABLE 0.1
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_1 + PG02_SE_P0012
;Operation: WG1_Touch4
LMOVE PG02_SE_TS_ID_2 + PG02_SE_P0014
SPEED 15 MM/S ALWAYS
CALL KR_TOUCH (&PG02_SE_P0015, &PG02_SE_TS_ID_2, ROTBASE_ON, 30.0, 15.0, 0)
STABLE 0.1
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_2 + PG02_SE_P0016
SPEED 50 ALWAYS
JMOVE PG02_SE_TS_ID_2 + PG02_SE_P0018
;Operation: WG1_Touch5
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_2 + PG02_SE_P0019
SPEED 15 MM/S ALWAYS
CALL KR_TOUCH (&PG02_SE_P0020, &PG02_SE_TS_ID_2, ROTBASE_ON, 30.0, 15.0, 0)
STABLE 0.1
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_2 + PG02_SE_P0021
;Operation: WG1_Touch6
LMOVE PG02_SE_TS_ID_2 + PG02_SE_P0023
SPEED 15 MM/S ALWAYS
CALL KR_TOUCH (&PG02_SE_P0024, &PG02_SE_TS_ID_2, ROTBASE_ON, 30.0, 15.0, 0)
STABLE 0.1
SPEED 200 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_2 + PG02_SE_P0025
;Operation: WG1_Seam7
SPEED 50 ALWAYS
JMOVE PG02_SE_TS_ID_1 + PG02_SE_P0027
SET_ARC_W1JOBNO 1 = 1
SETCONDW1 1 = 35,0,0,0,0,0,0,0
LWS PG02_SE_TS_ID_1 + PG02_SE_P0028 
LWE PG02_SE_TS_ID_2 + PG02_SE_P0029 ,1
SPEED 500 MM/S ALWAYS
LMOVE PG02_SE_TS_ID_2 + PG02_SE_P0030
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
PG02_SE_P0001 101.91 1092.98 1058.36 90 -135 -90 0 180
PG02_SE_P0002 101.91 1092.98 1028.36 90 -135 -90 0 180
PG02_SE_P0003 101.91 1092.98 1058.36 90 -135 -90 0 180
PG02_SE_P0005 160.47 1083.66 1001.93 35.26 -120 -125.26 0 180
PG02_SE_P0006 130.47 1083.66 1001.93 35.26 -120 -125.26 0 180
PG02_SE_P0007 160.47 1083.66 1001.93 35.26 -120 -125.26 0 180
PG02_SE_P0009 179.26 1162.12 1064.81 35.26 -120 -102.26 0 180
PG02_SE_P0010 101.92 1155.86 994.54 90 -135 -90 0 180
PG02_SE_P0011 101.92 1125.86 994.54 90 -135 -90 0 180
PG02_SE_P0012 101.92 1155.86 994.54 90 -135 -90 0 180
PG02_SE_P0014 -95.78 1155.86 992.08 90 -135 -90 0 180
PG02_SE_P0015 -95.78 1125.86 992.08 90 -135 -90 0 180
PG02_SE_P0016 -95.78 1155.86 992.08 90 -135 -90 0 180
PG02_SE_P0018 -149.62 1148.67 981.23 90 -135 -90 0 180
PG02_SE_P0019 -160.47 1082.59 1002.65 144.74 -120 -54.74 0 180
PG02_SE_P0020 -130.47 1082.59 1002.65 144.74 -120 -54.74 0 180
PG02_SE_P0021 -160.47 1082.59 1002.65 144.74 -120 -54.74 0 180
PG02_SE_P0023 -102.32 1092.74 1058.36 90 -135 -90 0 180
PG02_SE_P0024 -102.32 1092.74 1028.36 90 -135 -90 0 180
PG02_SE_P0025 -102.32 1092.74 1058.36 90 -135 -90 0 180
PG02_SE_P0027 118.75 1191.11 1093.61 90 -135 -90 0 180
PG02_SE_P0028 118.75 1120.4 1022.9 90 -135 -90 0 180
PG02_SE_P0029 -118 1120.4 1022.9 90 -135 -90 0 180
PG02_SE_P0030 -118 1191.11 1093.61 90 -135 -90 0 180
PG02_SE_TOOL1 2.2 141.71 431.71 -90 -45 90
.END
