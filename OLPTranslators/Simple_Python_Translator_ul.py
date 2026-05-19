import sys
from cenpyupload import Uploader
from cenpyupload import ULPythonUploadOperator
from cenpyupload import ULPythonPosition
from cenpyolpcore import InsertPosition
from cenpyolpcore import AttributeValueUnitType
from cenpydownload import MotionType
from cenpydownload import ProcessType
from cenpydownload import TargetType
import re
from io import TextIOWrapper
from enum import Enum

UPLOAD_CLASS_NAME = "SimplePythonUploader"
 

class AttributeLevel(Enum):
    Program = 1,
    Group = 2,
    Operation = 3,
    Event =4


class SimplePythonUploader(Uploader):
 

#region Uploader Base method overrides

    def __init__(self):
        super().__init__()
        self._programList = []

        self._baseProfileList = []
        self._toolProfileList = []
        self._allJointsList = []
 
    def Initialize(self, operator : ULPythonUploadOperator):
        logger = operator.GetLogOperator()
        logger.LogDebug("SimplePython Initialize called")

        controller = operator.GetController()

        self._baseProfileList = controller.GetBaseProfiles()
        self._toolProfileList = controller.GetToolProfiles()
        self._allJointsList = controller.GetConnectedJoints()
 
    def ParseFile(self, operator : ULPythonUploadOperator, fileObject : TextIOWrapper):
        logger = operator.GetLogOperator()
        logger.LogDebug("SimplePython ParseFile called")
       
        lines = fileObject.readlines()
 
        self.parseLines(operator, lines)
       
    def Finalize(self, operator : ULPythonUploadOperator):
        logger = operator.GetLogOperator()
        logger.LogDebug("SimplePython Finalize called")

#endregion

#region Uploader utilities methods

    def convertValue(self, value : str, targetType : str):
        """
        Coverts the input string value to the target type e.g. string to int or double etc...

        Parameters:
            value (str): Value to be converted
            targetType (str): target for conversion

        Returns:
            Converted value, in case of error we raise ValueError
        """
        max_unsigned_int = 2**32 - 1
        double_max = sys.float_info.max
        double_min = sys.float_info.min

        execptional_values = {
            "float min negative: -1.7976931348623157e+308": double_min,
            "float max: 1.7976931348623157e+308": double_max,
            "notDefined": max_unsigned_int
        }
        
        try:
            if targetType == 'int':
                return int(value)
            elif targetType == 'bool':
                if isinstance(value, str) and value.strip().lower() == 'true':
                    return True
                return False
            elif targetType == 'float':
                return round(float(value), 6)
            elif targetType == 'string':
                return str(value)
            else:
                raise ValueError(f"Unsupported target type: {targetType}")
        except (ValueError, TypeError):
            # If conversion fails, check if the value is in the dictionary
            if value in execptional_values:
                return execptional_values[value]
            else:
                raise ValueError(f"Unable to convert or find value: {value} with target type {targetType}")
        
    def convertArrayStrToValuesList(self, inputString, targetType):
        """
        Coverts the input string value list to the target type e.g. string to int or double etc...

        Parameters:
            inputString (list of str): Values to be converted
            targetType (str): target for conversion

        Returns:
            Converted values list, in case of error we raise ValueError
        """
        # Split the input string by commas to get individual values as strings
        values = inputString.split(',')

        # Convert each value to the specified type and collect them in a list
        try:
            converted_values = [self.convertValue(value.strip(), targetType) for value in values]
        except ValueError as e:
            raise ValueError(f"Error converting value: {e}")

        return converted_values

    attrPropertiesMap = {
         0:       "NoneValue",
         1 << 0: "UserAttribute",
         1 << 1: "ProcessAttribute",
         1 << 2: "OperationAttribute",
         1 << 3: "OperationGroupAttribute",
         1 << 4: "GlobalAttribute",
         1 << 5: "ReadOnlyAttribute",
         1 << 6: "ControllerAttribute"
    }

    def bitwiseFromMap(self, inputString, mapToConvert = attrPropertiesMap):
        """
        Converts a delimited string of attribute names into a cumulative bitwise value.

        Parameters:
            inputString (str): A string containing attribute names separated by '|'.
            mapToConvert (dict, optional): A dictionary mapping bitwise keys (int) to attribute names (str).
                Defaults to `attrPropertiesMap`.

        Returns:
            The cumulative bitwise, in case of error we raise ValueError
        """
        if len(inputString) == 0:
            return 0
        
        values = inputString.split('|')
        
        bitwiseSum = 0

        for value in values:
            value = value.strip() 
            found = False
            for bitwiseKey, stringValue in mapToConvert.items():
                if value == stringValue:
                    bitwiseSum |= bitwiseKey
                    found = True
                    break
            if not found:
                raise ValueError(f"Value '{value}' not found in the provided attribute map")

        return bitwiseSum   
    
    def getJointAndValues(self, connectedJoints, nameValuesJoints):
        """
        Maps joint objects to their respective values based on their names.
        Parameters:
            connectedJoints (list): A list of joint objects
            nameValuesJoints (list): A list of tuples, where each tuple consists of:
                                    - name (str): The name of the joint.
                                    - value: The corresponding value for the joint.

        Returns:
            list: A list of tuples where each tuple contains:
                - joint (object): A joint object from the `connectedJoints` list.
                - value: The corresponding value from `nameValuesJoints` for the joint's name.
                Only joints with names matching those in `nameValuesJoints` will be included.
        """
        name_value_dict = {name: value for name, value in nameValuesJoints}

        # Create the result list of pairs (joint, value)
        result_list = [(joint, name_value_dict[joint.GetName()]) for joint in connectedJoints if joint.GetName() in name_value_dict]

        return result_list
      
#endregion

    def parseLines(self, operator : ULPythonUploadOperator, lines: list):
        # Holds the current parsed program
        currentProgram = None
        # Holds the current parsed operation group
        currentOperationGroup = None
        # Holds the current parsed operation
        currentOperation = None
        # Holds the current parsed motion
        currentMotion = None
        #Holds the current parsed event
        currentEvent = None
        # Holds a list with all the events found before the motion
        eventsBefore = []
        # Flag which indicates if we currently parsing inside an event section
        isEventSection = False
        # Flag which indicates if we currently parsing inside an attribute section
        isAttributeSection = False
        # Flag which indicates on what attribute level we are at e.g. program, og etc..
        attributeLevel = None
        # Flag which indicates if we currently parsing inside an approach or retract event section
        isApproachRetractSection = False

        lineIterator = iter(lines)
        for line in lineIterator:
            # Parse the program
            program = self.parseProgram(operator, line)
            if program:
                currentProgram = program
                continue
            # Parse the operation group
            operationGroup = self.parseOperationGroup(operator, line)
            if operationGroup:
                currentOperationGroup = operationGroup
                if currentProgram:
                    currentProgram.AddOperationGroup(operationGroup)
                continue

            # Parse the operation
            operation = self.parseOperation(operator, line, lineIterator)
            if operation:
                currentOperation = operation
                if currentOperationGroup:
                    currentOperationGroup.AddOperation(operation)
                continue
            
            # Parse the motion
            motion = self.parseMotion(operator, line, lineIterator, isApproachRetractSection)
            if motion:
                currentMotion = motion
                # Check to see if the motion it was created by and approach or retract event, if so we can add it directly
                # to the current operation and its process type got changed to auxiliary
                if isEventSection and currentEvent:
                    currentOperation.AddMotion(motion)
                    isApproachRetractSection = False
                elif not isEventSection and currentOperation:
                    # If we get in here it means that we are done with the events before section of the current motion
                    # and we can set the cached event to the it plus add it to the current operation 
                    motion.SetEventsBefore(eventsBefore)
                    eventsBefore.clear()
                    currentOperation.AddMotion(motion)
                continue

            # Check to see if and event section starts or ends
            isEvent = self.isEventSectionStart(line)
            eventSectionEnd = self.isEventSectionEnd(line)

            # If the arive at the end of an event section set the flags accordingly 
            if eventSectionEnd:
                isEventSection = False
                currentEvent = None
                isEvent = False

            # Start parsing the events if we are entering or we are already inside an event section 
            if isEvent or isEventSection:
                isEventSection = True
                # Here we get the event back if found, it's insert position and if it is an approach or retract event
                isAproachOrRetract, insertPosition, event = self.parseEvent(operator, next(lineIterator, '') if isEvent else line)
                if event:
                    currentEvent = event

                    # Similar to the event section we need to set a flag if we are inside and aproach or retract event section
                    if isAproachOrRetract:
                        isApproachRetractSection = True
                    
                    # Approach and retract events are not currently supported in the C++ side so we need to skip them here for
                    # the moment
                    if(insertPosition == InsertPosition.InsertAfter and not isAproachOrRetract):
                        currentMotion.AddEventAfter(event)
                    if(insertPosition == InsertPosition.InsertBefore and not isAproachOrRetract):
                        eventsBefore.append(event)
                    continue

            # Check to see if we are entering/existing an atrtibute section
            isAttribute = self.isAttributeSectionStart(line)
            isAttributeEnd = self.isAttributeSectionEnd(line)
            if isAttributeEnd:
                isAttributeSection = False
                isAttribute = None
                attributeLevel = None

            if isAttribute or isAttributeSection:
                isAttributeSection = True
                ul_attribute = self.ParseAttribute(operator, next(lineIterator, '') if isAttribute else line)
                
                # Store the attribute level on the first entry 
                if isAttribute:
                    attributeLevel = isAttribute

                # Based on the attribute level we are in we add the attribute accordingly 
                if attributeLevel is AttributeLevel.Program and currentProgram:
                    currentProgram.AddAttribute(ul_attribute)
                if attributeLevel is AttributeLevel.Group and currentOperationGroup:
                    currentOperationGroup.AddAttribute(ul_attribute)
                if attributeLevel is AttributeLevel.Operation and currentOperation:
                    currentOperation.AddAttribute(ul_attribute)
                if attributeLevel is AttributeLevel.Event and currentEvent:
                    currentEvent.AddAttribute(ul_attribute)
                
                continue

    def ParseAttribute(self, operator: ULPythonUploadOperator, line: str):
        """
        Determines if the attribute line was found. If so it will create the python object and fill it 
        with the necessary data

        Parameters:
            operator (ULPythonUploadOperator): The python upload operator
            line (str): The current line to be parsed.

        Returns:
            ULPythonAttribute: The attribute object if created None otherwise.
        """
        ul_attribute = None
        attribute_props = re.findall(r'(\w+)\s*=\s*"([^"]*)";', line)  
        attribute_creator = operator.GetAttributeSetterOperator()     
        if attribute_props:
            attribute_dict = {}
            for prop in attribute_props:
                 name, value = prop
                 attribute_dict[name] = value
           
            attribute_type = attribute_dict['Type'] if 'Type' in attribute_dict.keys() else None
            # Value - int 
            # Minimum, maximum, stepsize - int
            if attribute_type == 'IntAttribute':
                ul_attribute = attribute_creator.CreateWritingIntAttributesObject()
                value = self.convertValue(attribute_dict['Value'], 'int') if 'Value' in attribute_dict.keys() else None
                if value:
                    ul_attribute.SetValue(value)
                minimum = self.convertValue(attribute_dict['Min'], 'int') if 'Min'in attribute_dict.keys() else None
                if minimum:
                    ul_attribute.SetMinimum(minimum)
                maximum = self.convertValue(attribute_dict['Max'], 'int') if 'Max'in attribute_dict.keys() else None
                if maximum:
                    ul_attribute.SetMaximum(maximum)
                step_size = self.convertValue(attribute_dict['StepSize'], 'int') if 'StepSize'in attribute_dict.keys() else None
                if step_size:
                    ul_attribute.SetStepSize(step_size)
            # Value - double 
            # Minimum, maximum - double
            # stepsize - int
            elif attribute_type == 'DoubleAttribute':
                ul_attribute = attribute_creator.CreateWritingDoubleAttributesObject()
                value = self.convertValue(attribute_dict['Value'], 'float') if 'Value'in attribute_dict.keys() else None
                if value:
                    ul_attribute.SetValue(value)
                minimum = self.convertValue(attribute_dict['Min'], 'float') if 'Min'in attribute_dict.keys() else None
                if minimum:
                    ul_attribute.SetMinimum(minimum)
                maximum = self.convertValue(attribute_dict['Max'], 'float') if 'Max'in attribute_dict.keys() else None
                if maximum:
                    ul_attribute.SetMaximum(maximum)
                step_size = self.convertValue(attribute_dict['StepSize'], 'float') if 'StepSize'in attribute_dict.keys() else None
                if step_size:
                    ul_attribute.SetStepSize(step_size)
            # Value - str
            elif attribute_type == 'StringAttribute':
                ul_attribute = attribute_creator.CreateWritingStringAttributesObject()
                value = attribute_dict['Value'] if 'Value'in attribute_dict.keys() else None
                if value:
                    ul_attribute.SetValue(value)
            # Value - bool
            elif attribute_type == 'BoolAttribute':
                ul_attribute = attribute_creator.CreateWritingBoolAttributesObject()
                value = self.convertValue(attribute_dict['Value'], 'bool') if 'Value'in attribute_dict.keys() else None
                if value:
                    ul_attribute.SetValue(value)
            # Value - str
            # values - str
            elif attribute_type == 'LiteralAttribute':
                ul_attribute = attribute_creator.CreateWritingLiteralAttributesObject()
                values = self.convertArrayStrToValuesList(attribute_dict['Values'], 'string') if 'Values'in attribute_dict.keys() else None
                if values:
                    ul_attribute.SetValues(values)
                value = attribute_dict['Value'] if 'Value' in attribute_dict.keys() else None
                if value:
                    ul_attribute.SetValue(value)
            # values - int
            elif attribute_type == 'IntArrayAttribute':
                ul_attribute = attribute_creator.CreateWritingIntArrayAttributesObject()
                values = self.convertArrayStrToValuesList(attribute_dict['Values'], 'int') if 'Values'in attribute_dict.keys() else None
                if values:
                    ul_attribute.SetValues(values)   
            # values - double 
            elif attribute_type == 'DoubleArrayAttribute':
                ul_attribute = attribute_creator.CreateWritingDoubleArrayAttributesObject()
                values = self.convertArrayStrToValuesList(attribute_dict['Values'], 'float') if 'Values'in attribute_dict.keys() else None
                if values:
                    ul_attribute.SetValues(values)   

            # values - str
            elif attribute_type == 'StringArrayAttribute':
                ul_attribute = attribute_creator.CreateWritingStringArrayAttributesObject()
                values = self.convertArrayStrToValuesList(attribute_dict['Values'], 'string') if 'Values'in attribute_dict.keys() else None
                if values:
                    ul_attribute.SetValues(values)   

            # Commom props for all the attributes  
            name = attribute_dict['Name'] if 'Name'in attribute_dict.keys() else None
            if name:
                ul_attribute.SetName(name)
            group_name = attribute_dict['GroupName'] if 'GroupName'in attribute_dict.keys() else None
            if group_name:
                ul_attribute.SetGroupName(group_name)
            readonly = self.convertValue(attribute_dict['ReadOnly'], 'bool') if 'ReadOnly'in attribute_dict.keys() else None
            if readonly:
                ul_attribute.SetReadOnly(readonly)
            olp_props = self.bitwiseFromMap(attribute_dict['GetOlpProperty']) if 'GetOlpProperty'in attribute_dict.keys() else None
            if olp_props:
                ul_attribute.SetOlpProperty(olp_props)

            unitType = getattr(AttributeValueUnitType, attribute_dict['ValueUnitType']) if 'ValueUnitType'in attribute_dict.keys() else AttributeValueUnitType.Standard
            ul_attribute.SetValueUnitType(unitType)
        return ul_attribute



    def isAttributeSectionStart(self, line):
        """
        Determines if we are entering an attribute section

        Parameters:
            line (str): The current line to be parsed.

        Returns:
            Enum which indicates on what level of attributes we are in, error case returns None
        """
        program_start = re.compile(r'Program\s*attributes') 
        group_start = re.compile(r'Group\s*attributes') 
        operation_start = re.compile(r'Operation\s*attributes') 
        event_start = re.compile(r'Attributes\s*set\s*on\s*event:')

        if program_start.search(line):
            return AttributeLevel.Program
        elif group_start.search(line):
            return AttributeLevel.Group
        elif operation_start.search(line):
            return AttributeLevel.Operation
        elif event_start.search(line):
            return AttributeLevel.Event
        
        return None
    
    def isAttributeSectionEnd(self, line):
        """
        Determines if we are exiting an event section

        Parameters:
            line (str): The current line to be parsed.

        Returns:
            A bool which indicates if we exit an event section
        """
        program_end = re.compile(r'End of attributes for program') 
        group_end = re.compile(r'End of attributes for operation group') 
        operation_end = re.compile(r'End of attributes for operation') 
        event_end = re.compile(r'End of attributes for event')

        if program_end.search(line) or group_end.search(line) or operation_end.search(line) or event_end.search(line):
            return True

        return False
 
    def parseProgram(self, operator : ULPythonUploadOperator, line: str):
        """
       Determines if the program line was found. If so it will create the python object and fill it 
       with the necessary data

        Parameters:
            operator (ULPythonUploadOperator): The python upload operator
            line (str): The current line to be parsed.

        Returns:
            ULPythonProgram: The program object if created, None otherwise
        """
        program_pattern = re.compile(r'^Program: (\w+) IsMainProgram = (\w+)')
        program = program_pattern.search(line)
        if program :
            program_name, program_is_main = program.groups()
            newProgram = operator.CreateEmptyProgram()
            newProgram.SetName(program_name)
            newProgram.SetIsMainProgram(bool(program_is_main))
            return newProgram
        return None
            
    def parseOperationGroup(self, operator : ULPythonUploadOperator, line: str):
        """
        Determines if the operation group line was found. If so it will create the python object and fill it 
        with the necessary data

        Parameters:
            operator (ULPythonUploadOperator): The python upload operator
            line (str): The current line to be parsed.

        Returns:
            ULPythonOperationGroup: The operation group object if created, None otherwise
        """
        operation_group_pattern = re.compile(r'Operation\s+group:\s*(\w+)')
        operationGroupFind = operation_group_pattern.search(line)
        if operationGroupFind:
            groupName = operationGroupFind.groups()[0]
            ulOperationGroup = operator.CreateEmptyOperationGroup()
            ulOperationGroup.SetName(groupName)
            return ulOperationGroup
        return None

    def parseOperation(self, operator : ULPythonUploadOperator, line: str, lineIterator):
        """
        Determines if the operation line was found. If so it will create the python object and fill it 
        with the necessary data

        Parameters:
            operator (ULPythonUploadOperator): The python upload operator
            line (str): The current line to be parsed.
            lineIterator (): line interator it will be used to advance the line

        Returns:
            ULPythonOperation: The operation object if created, None otherwise
        """
        operation_pattern = re.compile(
                            r'Operation:\s*'
                            r'(\w+)\s*'
                            r'OperationType\s*=\s*'
                            r'(\w+)')
        operation = operation_pattern.search(line)
        if operation :
            ulOperation = operator.CreateEmptyOperation()
            operation_name, operation_type = operation.groups()
            next(lineIterator, '')
            baseProfile = self.ParseForBaseProfile(next(lineIterator, ''))

            next(lineIterator, '')
            toolProfile = self.ParseForToolProfile(next(lineIterator, ''))
            ulOperation.SetName(operation_name)
            ulOperation.SetUsedBaseProfile(baseProfile)
            ulOperation.SetUsedToolProfile(toolProfile)
            return ulOperation
        
        return None
    
    def parseJoints(self, line : str):
        """
        Determines if the joint line was found. If so it will create the python object and fill it 
        with the necessary data

        Parameters:
            line (str): The current line to be parsed.

        Returns:
            ULPythonJoint, str: The joint object if created and the value, None, None otherwise
        """
        main_joint_pattern = re.compile(r'\s*MainJoint\s*=\s*"([^"]+)"')
        ext_joint_pattern = re.compile(r'\s*ExtJoint\s*=\s*"([^"]+)"')
        main_result = main_joint_pattern.search(line)
        ext_result = ext_joint_pattern.search(line)

        #We either found a main or external joint
        if main_result or ext_result:
            joint_props = re.findall(r'(\w+)\s*=\s*"([^"]*)";', line)  
            joint_dict = {}
            for prop in joint_props:
                 name, value = prop
                 joint_dict[name] = value

            # Check on the controller joint list for the current joint based on the name
            for joint in self._allJointsList:
                name  = joint_dict.get('MainJoint') or joint_dict.get('ExtJoint')
                if joint.GetName() == name:
                    return joint, joint_dict.get('Value')
                
        return None, None
        


    def parseTarget(self, ulPosition: ULPythonPosition, targetType: TargetType, line: str, lineIterator):
        """
        Determines if the target line was found. If found it will read the data and fill the position object with it

        Parameters:
            ulPosition (ULPythonPosition): parent position
            targetType (TargetType): target type
            line (str): The current line to be parsed.
            lineIterator (): line interator it will be used to advance the line
        """
        if targetType == TargetType.Cartesian:
            line = next(lineIterator, '')
            cartesian_pattern = re.compile(
                                       r'\s*X = "([^"]+)"'  
                                       r';\s*Y = "([^"]+)"'  
                                       r';\s*Z = "([^"]+)"'  
                                       r';\s*Rx = "([^"]+)"'
                                       r';\s*Ry = "([^"]+)"'  
                                       r';\s*Rz = "([^"]+)"')
            config_pattern = re.compile(r'\s*Config = "([^"]+)";\s*Turn = "([^"]+)"')

            cart = cartesian_pattern.search(line)
            if not cart:
               # old Downloader had output XY"X"rxryrz, try to get this if search failed
               cartesian_pattern = re.compile(
                                       r'\s*X = "([^"]+)"'  
                                       r';\s*Y = "([^"]+)"'  
                                       r';\s*X = "([^"]+)"'  
                                       r';\s*Rx = "([^"]+)"'
                                       r';\s*Ry = "([^"]+)"'  
                                       r';\s*Rz = "([^"]+)"')
               cart = cartesian_pattern.search(line)
            
            config = config_pattern.search(next(lineIterator, ''))

            if cart:
                x, y, z, rx, ry, rz = cart.groups()
                ulPosition.SetXYZ((float(x), float(y), float(z)))
                ulPosition.SetOrientation((float(rx), float(ry), float(rz)))

            if config:
                configString, turnString = config.groups()
                ulPosition.SetConfig(configString)
                ulPosition.SetTurn(turnString)
            # return  ...NO, continue with Check for external Axis
            
        # ...continue with Joint, ...check anyway, possible External Axis also for Cartesian
        if targetType == TargetType.Joint or targetType == TargetType.Cartesian:
            line = next(lineIterator, '')
            mainJointsList = []
            externalJointsList = []
 
            joint, value = self.parseJoints(line)
            
            #Skip to the joint target section
            while joint is None or value is None:
                line = next(lineIterator,'')
                joint, value = self.parseJoints(line)
            
            #We loop until we no longer find any joints
            iJ = 1
            while joint and value:           
                #Add each joint, value pair to its intended list
                if joint.IsExternal():
                    externalJointsList.append((joint, self.convertValue(value, 'float')))
                else:
                    mainJointsList.append((joint, self.convertValue(value, 'float')))
                
                if iJ >= len(self._allJointsList):
                    break # ....to avoid next iterator, might be needed afterwards
                line = next(lineIterator, '')
                joint, value = self.parseJoints(line)
                iJ += 1
            
            if targetType == TargetType.Joint or len(externalJointsList) > 0:
               # set the Joints. For Cartesian, only if it has external Joints
               ulPosition.SetExplicitMainJointValues(mainJointsList)
               ulPosition.SetExplicitExternalJointValues(externalJointsList)
            
        
    def parsePosition(self, operator : ULPythonUploadOperator, line: str, isApproachOrRetract: bool, motionType : str):
        """
        Determines if the position line was found. If so it will create the python object and fill it 
        with the necessary data

        Parameters:
            operator (ULPythonUploadOperator): The python upload operator
            line (str): The current line to be parsed.
            isApproachOrRetract (bool): indicates whether the position is an approach or retract
            motionType (str) : the motion type

        Returns:
            Pair of ULPythonPositions: First - the motion position
                                       Second - motion via point position if motion is circular
        """
        position_pattern = re.compile(r'PositionName = "([^"]+)";\s*ProcessType = "([^"]+)";\s*TargetType = "([^"]+)"')
        return_list = position_pattern.search(line)
        if return_list:
            position_name, positionProcessType, positionTargetType = return_list.groups()
            ulPosition = operator.CreateEmptyPosition()

            # For the moment since the aproach and retract events are not supported on the C++ side
            # the proccess type will be changed to auxiliary
            if not isApproachOrRetract:
                ulPosition.SetProcessType(getattr(ProcessType,positionProcessType))
            else:
                ulPosition.SetProcessType(getattr(ProcessType,"Auxiliary"))
            ulPosition.SetTargetType(getattr(TargetType,positionTargetType))
 
            # If the motion type is circular we need to take care of the viaPoint position as well
            if motionType == 'Circular':
                ulViaPosition = operator.CreateEmptyPosition()
                ulViaPosition.SetProcessType(getattr(ProcessType,positionProcessType))
                ulViaPosition.SetTargetType(getattr(TargetType,positionTargetType))
                return ulPosition, ulViaPosition

            return ulPosition, None

        return None, None  

    def parseMotion(self, operator : ULPythonUploadOperator, line: str, lineIterator, isApproachOrRetract : bool):
        """
        Determines if the motion line was found. If so it will create the python object and fill it 
        with the necessary data

        Parameters:
            operator (ULPythonUploadOperator): The python upload operator
            line (str): The current line to be parsed.
            lineIterator (): line interator it will be used to advance the line
            isApproachOrRetract (bool): indicates whether the motion is an approach or retract

        Returns:
            ULPythonMotion: The motion object if created, None otherwise
        """
        motion_pattern = re.compile(r'Motion:\s*(\w+);\s*MotionType = "([^"]+)"')
        motionResult = motion_pattern.search(line)
        if motionResult:
            motionName, motionType = motionResult.groups()
            ulMotion = operator.CreateEmptyMotion()
            ulMotion.SetName(motionName)
            ulMotion.SetMotionType(getattr(MotionType, motionType))
            position, viaPosition = self.parsePosition(operator, next(lineIterator, ''), isApproachOrRetract, motionType)
            if position:
                ulMotion.SetPosition(position)
                self.parseTarget(position, position.GetTargetType(), next(lineIterator, ''), lineIterator)
            if viaPosition:
                ulMotion.SetViaPosition(viaPosition)
                self.HandleViaPointPosition(next(lineIterator, ''), lineIterator, viaPosition)
                
            return ulMotion
        return None


    def HandleViaPointPosition(self, line : str, lineIterator, viaPosition : ULPythonPosition):
        """
        Handles the via point position
        Parameters:
            line (str): The current line to be parsed.
            lineIterator (): line interator it will be used to advance the line
            viaPosition (ULPythonPosition): indicates whether the motion is an approach or retract
        """
        via_point_pos_pattern = re.compile(r'\s*Via Point Position\s*=\s*"([^"]+)"')
        # check incoming Line
        result = via_point_pos_pattern.search(line)

        # We need to skip all that joints section to get to the via point cartesian target
        while result is None:
            line = next(lineIterator,'')
            if line.strip() == '':
               empty_line_count += 1
               if empty_line_count >= 10:
                     raise Exception("Too many empty lines encountered. Upload File seems to be at the End. Abort.")
            else:
               empty_line_count = 0  # Reset counter if a non-empty line is found
            result = via_point_pos_pattern.search(line)
        
        viaPointName = result.group(1)
        viaPosition.SetName(viaPointName)
        self.parseTarget(viaPosition, viaPosition.GetTargetType(), next(lineIterator, ''), lineIterator)

    def isEventSectionStart(self, line):
        """
        Determines if we are entering an event section

        Parameters:
            line (str): The current line to be parsed.

        Returns:
            A bool which indicates if we entered an event section
        """
        event_start_before_pattern = re.compile(
            r'Events before (\w+)'
            r'\s*motion'
        )

        event_start_after_pattern = re.compile(
            r'Events after (\w+)'
            r'\s*motion'
        )

        isBefore = event_start_before_pattern.search(line)
        if isBefore:
            return True
        
        isAfter = event_start_after_pattern.search(line)
        if isAfter:
            return True
        
        return False
    
    def isEventSectionEnd(self, line):
        """
        Determines if we are exiting an event section

        Parameters:
            line (str): The current line to be parsed.

        Returns:
            A bool which indicates if we exit an event section
        """
        event_start_before_pattern = re.compile(
            r'End Events before (\w+)'
            r'\s*motion'
        )

        event_start_after_pattern = re.compile(
            r'End Events after (\w+)'
            r'\s*motion'
        )

        isBefore = event_start_before_pattern.search(line)
        if isBefore:
            return True
        
        isAfter = event_start_after_pattern.search(line)
        if isAfter:
            return True
        
        return False
    
    def parseEvent(self, operator : ULPythonUploadOperator, line):
        """
        Determines if the event line was found. If so it will create the python object and fill it 
        with the necessary data

        Parameters:
            operator (ULPythonUploadOperator): The python upload operator
            line (str): The current line to be parsed.

        Returns:
            ULPythonEvent: The event object if created, None otherwise
        """
        event_pattern = re.compile(
            r'EventName = "([^"]+)"'
            r';\s*EventGroupName = "([^"]+)"'
            r';\s*InsertPosition = "([^"]+)"'
            r';\s*EventType = "([^"]+)"'
        )
        insertPosition = InsertPosition.InsertNone
        event = event_pattern.search(line)
        if event:
            eventName, eventGroupName, insertPositionStr, eventTypeStr = event.groups()
            ulEvent = operator.CreateEmptyEvent()
            ulEvent.SetName(eventName)

            try:
                insertPosition = getattr(InsertPosition,insertPositionStr)
            except:
                insertPosition = InsertPosition.InsertNone
                operator.GetLogOperator().LogError("Wrong insert postion on event " + eventName)
            
            ulEvent.SetInsertPosition(insertPosition)
            if eventTypeStr in ["Approach", "Retract"]:
                return (True, insertPosition, ulEvent)
            
            return (False, insertPosition, ulEvent)
        return (False, insertPosition, None)

    def ParseForToolProfile(self, line):
        """
        Determines if the tool profile line was found. 

        Parameters:
            line (str): The current line to be parsed.

        Returns:
            ULPythonToolProfile: The tool profile object if created, None otherwise
        """
        tp_pattern = re.compile(
            r'ToolProfile = "([^"]+)"'
            r';\s*ProfileIndex = "([^"]+)"'
            r';\s*ToolType = "([^"]+)"'
            r';\s*X = "([^"]+)"'
            r';\s*Y = "([^"]+)"'
            r';\s*Z = "([^"]+)"'
            r';\s*Rx = "([^"]+)"'
            r';\s*Ry = "([^"]+)"'
            r';\s*Rz = "([^"]+)"'  )
       

        # Check in the found tool profile exist in the list of program tool profiles 
        profileResult = tp_pattern.search(line)
        if profileResult:
            profileName = profileResult.groups()[0]
            return next((x for x in self._toolProfileList if x.GetName() == profileName), None)
        
        return None
   
    def ParseForBaseProfile(self, line):
        """
        Determines if the base profile line was found.

        Parameters:
            line (str): The current line to be parsed.

        Returns:
            ULPythonBaseProfile: The base profile object if created, None otherwise
        """
        bp_pattern = re.compile(
                r'BaseProfile = "([^"]+)"'  
                r';\s*ProfileIndex = "([^"]+)"'  
                r';\s*ReferenceProfile = "([^"]+)"'  
                r';\s*X = "([^"]+)"'  
                r';\s*Y = "([^"]+)"'  
                r';\s*Z = "([^"]+)"'  
                r';\s*Rx = "([^"]+)"'
                r';\s*Ry = "([^"]+)"'  
                r';\s*Rz = "([^"]+)"'  )
        
        # Check in the found base profile exist in the list of program base profiles 
        profileResult = bp_pattern.search(line)
        if profileResult:
            profileName = profileResult.groups()[0]
            return next((x for x in self._baseProfileList if x.GetName() == profileName), None)
 
        return None
   