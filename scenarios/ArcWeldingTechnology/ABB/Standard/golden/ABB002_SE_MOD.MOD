%%%
  VERSION:1
  LANGUAGE:ENGLISH
%%%
MODULE ABB002_SE_MOD

! Cenit E2 Program: ABB002_SE
  TASK PERS partdata pd_ABB002_SE:=["ABB002_SE","Comment","",0,0,"",""];

  LOCAL PERS pose peDisp1 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_mea1 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose tid_mea2 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS pose peDisp2 := [[0,0,0],[1,0,0,0]];
  LOCAL PERS jointtarget JP001:=[[0.000,0.000,0.000,0.000,90.000,0.000],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P002:=[[109.698,105.099,135.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P003:=[[109.698,105.099,105.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P004:=[[109.698,105.099,135.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P006:=[[160.506,101.443,84.746],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P007:=[[130.506,101.443,84.746],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P008:=[[160.506,101.443,84.746],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P010:=[[109.932,-110.011,135.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P011:=[[109.932,-110.011,105.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P012:=[[109.932,-110.011,135.506],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P014:=[[101.379,-160.506,85.643],[0.000000,0.500000,-0.707107,-0.500000],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P015:=[[101.379,-130.506,85.643],[0.000000,0.500000,-0.707107,-0.500000],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P016:=[[101.379,-160.506,85.643],[0.000000,0.500000,-0.707107,-0.500000],[-1,-1,1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P018:=[[160.506,-101.923,85.313],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P019:=[[130.506,-101.923,85.313],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P020:=[[160.506,-101.923,85.313],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P022:=[[160.355,-118.750,135.355],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P023:=[[125.000,-118.750,100.000],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P024:=[[125.000,118.000,100.000],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget P025:=[[160.355,118.000,135.355],[0.270598,0.653281,-0.653281,-0.270598],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS jointtarget JP026:=[[0.000,0.000,0.000,0.000,90.000,0.000],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  ! SEAMDATA declarations
  LOCAL PERS seamdata sm1:=[0.5,0.2,[0,0,0,0,0,0,0,0,0],0,1,0,0,0,[0,0,0,0,0,0,0,0,0],0,0,[0,0,0,0,0,0,0,0,0],0,0,[0,0,0,0,0,0,0,0,0],0.2];

  ! WELDDATA declarations
  LOCAL PERS welddata wd_default:=[7,0,[29,0,0,0,0,230,0,0,0],[0,0,0,0,0,0,0,0,0]];

  ! WEAVEDATA declarations
  LOCAL PERS weavedata wv_default:=[1,0,4,5,0,0,0,0,0,0,0,0,0,0,0];

  ! TRACKDATA declarations
  LOCAL PERS trackdata tr_default:=[0,FALSE,0,[0,25,30,0,0,0,0,0,0],[0,0,0,0,0,0,0]];

  PROC ABB002_SE()
    ! ABB Configuration
    ConfJ\On;
    ! Operation: WG1_Touch1
    MoveAbsJ JP001,v1000,fine,TOOL1\WObj:=BF;
    MoveJ P002,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_mea1,P002,P003,v50,TOOL1\Wobj:=BF;
    MoveL P004,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch2
    MoveJ P006,v1000,fine,TOOL1\WObj:=BF;
    Search_1D peDisp2,P006,P007,v50,TOOL1\Wobj:=BF\PrePDisp:=tid_mea1;
    MoveL P008,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch3
    MoveJ P010,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_mea1,P010,P011,v50,TOOL1\Wobj:=BF;
    MoveL P012,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch4
    MoveJ P014,v1000,fine,TOOL1\WObj:=BF;
    Search_1D tid_mea2,P014,P015,v50,TOOL1\Wobj:=BF\PrePDisp:=tid_mea1;
    MoveL P016,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Touch5
    MoveJ P018,v1000,fine,TOOL1\WObj:=BF;
    Search_1D peDisp1,P018,P019,v50,TOOL1\Wobj:=BF\PrePDisp:=PoseAdd(tid_mea1,tid_mea2);
    MoveL P020,v1000,fine,TOOL1\WObj:=BF;
    ! Operation: WG1_Seam6
    PDispSet peDisp1;
    MoveJ P022,v1000,fine,TOOL1\WObj:=BF;
    ArcLStart P023,v500,sm1,wd_default\Weave:=wv_default,fine,TOOL1\WObj:=BF\Track:=tr_default;
    PDispSet peDisp2;
    ArcLEnd P024,v30,sm1,wd_default\Weave:=wv_default,fine,TOOL1\WObj:=BF\Track:=tr_default;
    MoveL P025,v500,z100,TOOL1\WObj:=BF;
    MoveAbsJ JP026,v1000,fine,TOOL1\WObj:=BF;
    PDispOff;
  EndProc
ENDMODULE
