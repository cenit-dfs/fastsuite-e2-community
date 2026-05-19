from dataclasses import dataclass

@dataclass
class ArcOnInfo:
   OTC_WELD_ON_PRGNR: str = "1"
   OTC_WELD_OFF_PRGNR: str = "1"
   OTC_WELD_CHARACTER: str = "4"
   OTC_WIRE_FEED: str = "22"
   OTC_CURRENT: str = "160"
   OTC_VOLTAGE: str = "28"
   OTC_USE_WEAVE: bool = False
   OTC_WEAVE_COND_NR: str = "1"
   ArcSenseSt: bool = False
   ArcSenseStCondFile: str = "1"
   ArcSenseStSampleData: str = "0"
   ArcSenseEtCondFile: str = "0"
   OTC_STITCH_PULSE_ENABLED: bool = False
   OTC_STITCH_PULSE_AS_COND: str = "1"
   OTC_STITCH_PULSE_AE_COND: str = "1"
   OTC_STITCH_PULSE_WELDING_TIME: str = "0.7"
   OTC_STITCH_PULSE_COOLING_TIME: str = "0.2"
   OTC_STITCH_PULSE_MOVEMENT_PITCH: str = "0.004"
   OTC_STITCH_PULSE_MOVE_COND_NUMBER: str = "0"
   ruleEvent: str = "1"

# Daihen PowerSource Parameters
@dataclass
class ArcOnWBPL:
   AS_Cond_file: str = "0"
   Retry: str = "0"
   Version: str = "2"
   Characteristic_data_registration_number: str = "1"
   Welding_process: str = "0"
   Current_condition_type: str = "1"
   Voltage_adjustment_method: str = "1"
   Slope_condition_type: str = "0"
   Welding_control_type: str = "0"
   Cold_tandem: str = "0"
   Robot_RS_file_number: str = "-1"
   Robot_operating_condition_number: str = "0"
   Melt_adjustment: str = "0"
   Welding_current: str = "0"
   Welding_current_High: str = "0"
   Welding_voltage: str = "0"
   Welding_voltage_High: str = "0"
   Welding_speed: str = "0"
   Arc_characteristics_short: str = "0"
   Arc_characteristics_short_High: str = "0"
   Arc_characteristics_arc: str = "0"
   Arc_characteristics_arc_High: str = "0"
   
@dataclass
class ArcOffWBPL:
   AE_Cond_file: str = "0"
   Version: str = "2"
   Characteristic_data_registration: str = "1"
   Welding_process: str = "0"
   Current_condition_type: str = "1"
   Voltage_adjustment_method: str = "1"
   Slope_condition_type: str = "0"
   Wire_retract: str = "0"
   Welding_current: str = "0"
   Crater_voltage: str = "0"
   Crater_time: str = "0"
   Post_flow_time: str = "0"
   Pulse_arc_characteristic: str = "0"
   Arc_characteristic_1_Short: str = "0"
   Arc_characteristic_2_Arc: str = "0"
   
@dataclass
class ArcOnDPAX:
   AS_Cond_file: str = "1"
   Retry: str = "0"
   Version: str = "1"
   Characteristic_data_registration_number: str = "1"
   Welding_process: str = "0"
   Current_condition_type: str = "1"
   Voltage_adjustment_method: str = "1"
   Slope_condition_kind: str = "0"
   Welding_current: str = "0"
   Welding_voltage: str = "0"
   Slope_time: str = "0"
   Welding_speed: str = "0"
   Welding_current_2: str = "0"
   Welding_voltage_2: str = "0"
   Initial_welding_current: str = "0"
   Initial_welding_voltage: str = "0"

@dataclass
class ArcOffDPAX:
   AE_Cond_file: str = "1"
   Version: str = "1"
   Characteristic_data_registration: str = "1"
   Welding_process: str = "0"
   Current_condition_kind: str = "1"
   Voltage_adjustment_method: str = "1"
   Slope_condition_kind: str = "0"
   Welding_current: str = "0"
   Crater_voltage: str = "0"
   Slope_time: str = "0"
   Crater_time: str = "0"
   After_flow_time: str = "0"
   Wave_frequency: str = "0"
   Penetration_adjustment: str = "0"
   Base_current: str = "0"

@dataclass
class ArcOnDA:
   AS_Cond_file: str = "0"
   Retry: str = "0"
   Version: str = "2"
   Characteristic_data_registration_number: str = "1"
   Output_current: str = "0"
   AC_waveform: str = "0"
   Power_source_kind: str = "7"
   Slope_condition_kind: str = "0"
   Filler_control: str = "0"
   Welding_current: str = "0"
   Peak_current: str = "0"
   Slope_time: str = "0"
   Welding_speed: str = "0"
   Filler_wire_feed_rate: str = "0"
   Filler_wire_feed_rate_at_peak: str = "0"

@dataclass
class ArcOffDA:
   AE_Cond_file: str = "1"
   Version: str = "2"
   Characteristic_data_registration: str = "0"
   Current_output: str = "1"
   AC_waveform: str = "0"
   Power_source_kind: str = "7"
   Slope_condition_kind: str = "0"
   Crater_current: str = "0"
   Retract_speed: str = "0"
   Slope_time: str = "0"
   Crater_time: str = "0"
   After_flow_time: str = "0"
   Retract_time: str = "0"

# ArcSensing ST/ET
@dataclass
class ArcOnST:
   AS_Cond_file: str = "1"
   ST_Cond_file: str = "1"
   Sample_data_No: str = "1"
   Tracking_Sensitivity_Horizontal: str = "1"
   Tracking_Sensitivity_Vertical: str = "1"
   Tracking_Offset_Horizontal_mm: str = "0"
   Tracking_Offset_Vertical_mm: str = "0"
   Chasing_coordinates: str = "Torch"
   Tracking_deviation_Range_mm: str = "0"
   Number_of_direction_groove: str = "0"
   Arc_stable_surveillance_value: str = "0"
   Wire_feed_stable_surveillance_value: str = "0"
   Arc_standard_voltage: str = "0"
   Base_voltage: str = "0"
   Tracking_Time_Vertical_sec: str = "0"
   Tracking_Time_Horizontal_sec: str = "0"
   Effect_Voltage_Low_V: str = "0"
   Effect_Voltage_High_V: str = "0"
   Current_Response_A: str = "0"
   Tracking_ON_OFF: str = "ON"
   ST_command_version: str = "2"

@dataclass
class ArcOffET:
   AE_Cond_file: str = "1"
   ET_Cond_file: str = "1"
   Store_No: str = "999"
   End_Point_Detection: str = "Disabled"
   End_Point_Offset_mm: str = "0"
   End_Point_Detection_Range_mm: str = "0"
   Store_Coordinates: str = "Machine"
   Basement_of_Store: str = "Teach Point"
   Keep_compensation: str = "Disabled"

@dataclass
class ArcOnZN:
   ZN_GFF: str = "999"
   ZN_LSR: str = "999"
   ZN_OFFSET: str = "-10"
   ZN_SEARCH_RANGE: str = "100"

@dataclass
class ArcOffZF:
   ZF_GFF: str = "999"
   ZF_LSR: str = "999"
   ZF_POSITION: str = "1000"
   ZF_POSTURE: str = "900"
   ZF_STORE_NUM: str = "810"
   ZF_STORE_COORD: str = "1"
   ZF_SEARCH_RANGE: str = "1000"
   ZF_OFFSET: str = "0"
   ZF_SPEED: str = "8.333"

@dataclass
class ArcOnZT:
   AS_Cond_file: str = "1"
   ZT_GFF: str = "999"
   ZT_LSR: str = "999"
   ZT_POSITION: str = "100"
   ZT_POSTURE: str = "90"

@dataclass
class ArcOffZE:
   AE_Cond_file: str = "1"
   ZE_STORE_NUM: str = "8"
   ZE_STORE_COORD: str = "5"
   ZE_OVER_DEV_RANGE: str = "1000"

@dataclass
class ArcOnZJ:
   GFF: str = "999"
   GAP: str = "10"
   Search_Waiting_Time: str = "0.1"
   Stable_Waiting_Time: str = "1.0"
   Store_Coordinates: str = "5"
   Over_Deviation_Range: str = "100.0"
   Gap_watch_MAX: str = "350.0"
   Gap_watch_MIN: str = "-50.0"
   Min_depth_value: str = "20.0"
   Groove_angle1_MAX: str = "150"
   Groove_angle1_MIN: str = "0.0"
   Groove_angle2_MAX: str = "150"
   Groove_angle2_MIN: str = "0.0"
   Groove_angle1: str = "90"