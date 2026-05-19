# -------------------------------------------------------------------------------------------
# Name: LaserFovEvent
# Description: Moves the line laser's FOV representation relative to the weld TCP
#              Customize the two attributes to your own resource
#              RESOURCE_NAME          : Resource name
#              JOINT_VALUE_ATTRIBUTES : list of double attributes
#              The number of joint ports and the number of attributes need to match
# Debug info: E2@localhost:5254
# Author: Berauer
# Changelog:
#     Version: 1.0
#        Changed by:
#        Date:
#
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
from cenpylib import *
import sys

sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "LaserFovEvent.py: "
RESOURCE_NAME = "LaserScannerFOV"
JOINT_VALUE_ATTRIBUTES = [
    "LaserFovX",
    "LaserFovY",
    "LaserFovZ",
    "LaserFovA",
    "LaserFovB",
    "LaserFovC",
]

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = (
    "(Debug-Technology-Technology) initialization of attributes ended."
)

DEBUG_POST_PROCESS_ATTRIB_START = (
    "(Debug-Technology) event post process attrib started."
)
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug-Technology) event post process attrib ended."

DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START = (
    "(Debug-Technology) event post process upload attrib started."
)
DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END = (
    "(Debug-Technology) event post process upload attrib ended."
)

DEBUG_POST_EVENT_COMPUTE_START = "(Debug-Technology) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug-Technology) event post compute ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = (
    "(Debug-Technology) post on attribute change started."
)
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) prev on attribute change ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."


# -------------------------------------------------------------------------------------------
# post event compute
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
    # get logger
    logging = Operator.GetLoggerOperator()
    # debug logging
    logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
    # get attribute getter
    attribGetter = Operator.GetAttribGetter()
    # get event operator
    eventOperator = Operator.GetEventOperator()
    # get reference toolpath element
    refTpElement = Operator.GetRefTpElement()
    # get controller
    controller = Operator.GetController()
    # check none
    if (
        (attribGetter == None)
        or (eventOperator == None)
        or (refTpElement == None)
        or (controller == None)
    ):
        logging.LogError(
            RESOURCE_NAME + ": Python, zero pointer initialization PostCompute"
        )
    else:
        resPortEvent = eventOperator.AddSetResourcePortEvent(
            refTpElement, TPINSERTPOS_INSERTBEFORE
        )
        resources = controller.GetResources(FSITEMTYPE_PRODUCTION, SUBITEM_NONE)
        for r in range(0, len(resources)):
            olpResource = resources[r]
            if olpResource.GetName() == RESOURCE_NAME:
                # Retrieve double values using list comprehension
                jointVals = [
                    attribGetter.GetDouble(target) for target in JOINT_VALUE_ATTRIBUTES
                ]
                # Get only the ports of type joint (2) and only IN (0) direction
                jointPorts = olpResource.GetPorts(2, 0)
                if not (len(jointVals) == len(jointPorts)):
                    logging.LogError(
                        "Joint Port # ("
                        + str(len(jointVals))
                        + ") not equal to"
                        + "Joint Value #("
                        + str(len(jointPorts))
                        + ")"
                    )
                else:
                    # Set the resource for the event
                    resPortEvent.SetResource(olpResource)
                    # Iterate over the ports and their corresponding values using zip
                    for jointPort, jointVal in zip(jointPorts, jointVals):
                        # Add the port float value to the event
                        resPortEvent.AddResourcePortFloat(jointPort, jointVal)


# -------------------------------------------------------------------------------------------
#
def GetEventName():
    return "LaserFovEvent"


# Set UUID mandatory
def GetEventUuId():
    return "0D196218-D99F-461F-8C41-06278F654123"


def GetIconName():
    return "Circle"


def GetEventType():
    return OLPEVENT_OLP


def IsEnabled():
    return False
