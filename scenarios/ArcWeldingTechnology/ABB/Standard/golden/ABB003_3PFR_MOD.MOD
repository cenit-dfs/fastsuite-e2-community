%%%
  VERSION:1
  LANGUAGE:ENGLISH
%%%
MODULE ABB003_3PFR_MOD

! Cenit E2 Program: ABB003_3PFR
  TASK PERS partdata pd_ABB003_3PFR:=["ABB003_3PFR","Comment","",0,0,"",""];

  LOCAL PERS wobjdata obNEW_1 := [FALSE, FALSE, "STNNone", [[0,0,0],[1,0,0,0]], [[0,0,0],[1,0,0,0]]];
  LOCAL PERS robtarget pRef1 := [[134.69,-136.16,50.51],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget pRef2 := [[130.51,101.52,63.61],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget pRef3 := [[-109.03,57.60,105.50],[0.382325,0.565545,-0.730556,-0.016560],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS pose pMea1 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose pMea2 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose pMea3 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_pt1_mea1 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_pt1_mea2 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_pt1_mea3 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_pt2_mea1 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_pt2_mea2 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_pt3_mea1 := [[0,0,0],[1,0,0,0]];

  LOCAL PERS jointtarget JP001:=[[0.000,0.000,0.000,-0.000,90.000,0.000],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P002:=[[134.692,-136.156,80.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P003:=[[134.692,-136.156,50.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P004:=[[134.692,-136.156,80.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P006:=[[103.438,-160.506,70.480],[0.000000,0.500000,-0.707107,-0.500000],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P007:=[[103.438,-130.506,70.480],[0.000000,0.500000,-0.707107,-0.500000],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P008:=[[103.438,-160.506,70.480],[0.000000,0.500000,-0.707107,-0.500000],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P010:=[[160.506,-103.845,71.768],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P011:=[[130.506,-103.845,71.768],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P012:=[[160.506,-103.845,71.768],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P014:=[[160.506,101.517,63.612],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P015:=[[130.506,101.517,63.612],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P016:=[[160.506,101.517,63.612],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P018:=[[142.215,108.224,80.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P019:=[[142.215,108.224,50.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P020:=[[142.215,108.224,80.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P022:=[[-109.028,57.599,135.503],[0.382325,0.565545,-0.730556,-0.016560],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P023:=[[-109.028,57.599,105.503],[0.382325,0.565545,-0.730556,-0.016560],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P024:=[[-109.028,57.599,135.503],[0.382325,0.565545,-0.730556,-0.016560],[0,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P026:=[[165.355,-118.000,85.355],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P027:=[[130.000,-118.000,50.000],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P028:=[[130.000,-61.213,50.000],[0.265854,0.664538,-0.641827,-0.275261],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P029:=[[130.000,-55.473,51.142],[0.151521,0.672665,-0.611688,-0.387815],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P030:=[[130.000,-50.607,54.393],[0.008691,0.698309,-0.512215,-0.499924],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P031:=[[130.000,-29.393,75.607],[0.008691,0.698309,-0.512215,-0.499924],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P032:=[[130.000,-24.527,78.858],[0.124211,0.713537,-0.563477,-0.397405],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P033:=[[130.000,-18.787,80.000],[0.265854,0.664538,-0.641827,-0.275261],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P034:=[[130.000,18.787,80.000],[0.275262,0.641827,-0.664538,-0.265852],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P035:=[[130.000,24.527,78.858],[0.387816,0.611686,-0.672667,-0.151520],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P036:=[[130.000,29.393,75.607],[0.499924,0.512215,-0.698309,-0.008691],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P037:=[[130.000,50.607,54.393],[0.499924,0.512215,-0.698309,-0.008691],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P038:=[[130.000,55.473,51.142],[0.397405,0.563477,-0.713537,-0.124211],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P039:=[[130.000,61.213,50.000],[0.275261,0.641827,-0.664538,-0.265854],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P040:=[[130.000,118.000,50.000],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P041:=[[165.355,118.000,85.355],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P042:=[[2.200,-141.214,348.286],[0.382683,0.923880,0.000004,-0.000001],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  ! SEAMDATA declarations
  LOCAL PERS seamdata sm1:=[0.5,0.2,[0,0,0,0,0,0,0,0,0],0,1,0,0,0,[0,0,0,0,0,0,0,0,0],0,0,[0,0,0,0,0,0,0,0,0],0,0,[0,0,0,0,0,0,0,0,0],0.2];

  ! WELDDATA declarations
  LOCAL PERS welddata wd_default:=[7,0,[29,0,0,0,0,230,0,0,0],[0,0,0,0,0,0,0,0,0]];

  ! WEAVEDATA declarations
  LOCAL PERS weavedata wv_default:=[1,0,4,5,0,0,0,0,0,0,0,0,0,0,0];

  ! TRACKDATA declarations
  LOCAL PERS trackdata tr_default:=[0,FALSE,0,[0,25,30,0,0,0,0,0,0],[0,0,0,0,0,0,0]];

  PROC ABB003_3PFR()
    ! ABB Configuration
    ConfJ\On;
    ! Operation: WG1_Touch1
    MoveAbsJ JP001,v1000,fine,TOOL1\WObj:=BF;
    MoveJ P002,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_pt1_mea1,P002,P003,v50,TOOL1\Wobj:=BF;
    MoveL P004,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch2
    MoveJ P006,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_pt1_mea2,P006,P007,v50,TOOL1\Wobj:=BF\PrePDisp:=tid_pt1_mea1;
    MoveL P008,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch3
    MoveJ P010,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_pt1_mea3,P010,P011,v50,TOOL1\Wobj:=BF\PrePDisp:=PoseAdd(tid_pt1_mea1,tid_pt1_mea2);
    MoveL P012,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch4
    MoveJ P014,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_pt2_mea1,P014,P015,v50,TOOL1\Wobj:=BF;
    MoveL P016,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch6
    MoveJ P018,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_pt2_mea2,P018,P019,v50,TOOL1\Wobj:=BF\PrePDisp:=tid_pt2_mea1;
    MoveL P020,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch7
    MoveJ P022,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_pt3_mea1,P022,P023,v50,TOOL1\Wobj:=BF;
    MoveL P024,v1000,fine,TOOL1\WObj:=BF;
    pMea1 := tid_pt1_mea3;
    pMea2 := tid_pt2_mea2;
    pMea3 := tid_pt3_mea1;
    obNEW_1 := OFrameChange(BF, pRef1, pRef2, pRef3, pMea1, pMea2, pMea3);
    ! Operation: WG1_Seam8
    ! Activating TS Frame WObj: obNEW_1
    MoveJ P026,v1000,fine,TOOL1\WObj:=obNEW_1;
    ArcLStart P027,v500,sm1,wd_default\Weave:=wv_default,fine,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcL P028,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcC P029,P030,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcL P031,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcC P032,P033,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcL P034,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcC P035,P036,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcL P037,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcC P038,P039,v30,sm1,wd_default\Weave:=wv_default,z100,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    ArcLEnd P040,v30,sm1,wd_default\Weave:=wv_default,fine,TOOL1\WObj:=obNEW_1\Track:=tr_default;
    MoveL P041,v500,z100,TOOL1\WObj:=obNEW_1;
    MoveL P042,v500,z100,TOOL1\WObj:=obNEW_1;
    PDispOff;
  EndProc
ENDMODULE
