# Generic libraries
import os, re
import math
import numpy as np
from io import TextIOWrapper
import xml.etree.ElementTree as ET
from dataclasses import dataclass
# Cenit libraries
from centypes import *
from cenpylib import *
from cenpymath import *
from cenpyupload import *
from cenpyolpcore import *
from cenpymath import Matrix, Point3D, Converter, Notations
from cenpydownload import MotionType, ProcessType, TargetType
from cenpyunits import Angle
from enum import Enum

# Global constants
LCP_WORKING_TYPE_LITERALS = ["2D part-program", "3D part-program", "Bevel cutting", "Tube cutting", "Welding"]
LCP_TABLE_TYPE_LITERALS = ["FixedTable", "Roto-Tilt 0 (along Z)", "Roto-Tilt 90 (along X)", "Avionic"]
LCP_TUBE_TYPE_LITERALS = ["Round tube", "Square or rect. tube"]
LCP_CUTTING_TYPE_LITERALS = ["CUTTING", "MARKING", "WELDING"]
LCP_TECHNICAL_PARAM_TYPE_LITERALS = ["1 Easy", "2 Medium", "3 Hard", "4 Special", "5 Fast"]
LCP_PIERCING_TYPE_LITERALS = [
    "1:normal piercing",
    "2:no piercing",
    "3:quick piercing",
    "4:piercing with prehole",
    "5:enable cutting parameters",
    "11:normal piercing and cut with sensor locked",
    "12:no piercing and cut with sensor locked",
    "13:quick piercing and cut with sensor locked",
    "14:piercing with prehole and cut with sensor locked"
]

UPLOAD_CLASS_NAME = "PrimaXmlUploader"

class AttributeLevel(Enum):
    Program = 1,
    Group = 2,
    Operation = 3,
    Event =4

class BaseParser:
    """
    Base class providing common parsing utilities.
    """

    @staticmethod
    def normalize_vector(vector):
        norm = np.linalg.norm(vector)
        if norm == 0:
            return np.zeros_like(vector)
        return vector / norm

    @staticmethod
    def compute_rotation_matrix_ca(theta_c, theta_a):
        """
        Calculate rotation matrix for XYZCA-type kinematic.
        Args:
            theta_c (float): Rotation about Z axis in radians.
            theta_a (float): Rotation about X axis in radians.
        Returns:
            np.ndarray: The combined rotation matrix.
        """
        r_c = np.array([
            [np.cos(theta_c), -np.sin(theta_c), 0],
            [np.sin(theta_c), np.cos(theta_c), 0],
            [0, 0, 1],
        ])

        r_a = np.array([
            [1, 0, 0],
            [0, np.cos(theta_a), -np.sin(theta_a)],
            [0, np.sin(theta_a), np.cos(theta_a)],
        ])

        return np.dot(r_c, r_a)

    @staticmethod
    def extract_euler_angles(rotation_matrix):
        """
        Extract Euler angles (Z-Y-X convention) from a rotation matrix with explicit handling for theta_a = 0.
        Args:
            rotation_matrix (np.ndarray): 3x3 rotation matrix.
        Returns:
            tuple: (psi, theta, phi) Euler angles in degrees (Z-Y-X order).
        """
        # Check if the rotation matrix represents a pure Z rotation (theta_a = 0)
        is_pure_z_rotation = (
            abs(rotation_matrix[2, 0]) < 1e-6 and 
            abs(rotation_matrix[2, 1]) < 1e-6 and 
            abs(rotation_matrix[2, 2] - 1.0) < 1e-6
        )

        if is_pure_z_rotation:
            # Special case: Pure Z rotation
            psi = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])  # Rotation about Z
            theta = 0  # No Y rotation
            phi = 0  # No X rotation
            return float(np.degrees(psi)), float(np.degrees(theta)), float(np.degrees(phi))

        # General case decomposition
        sy = math.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        singular = sy < 1e-6

        if not singular:
            phi = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])  # Rotation about X
            theta = math.atan2(-rotation_matrix[2, 0], sy)                 # Rotation about Y
            psi = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0]) # Rotation about Z
        else:
            # Handle singular case
            phi = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])  # Rotation about X
            theta = math.atan2(-rotation_matrix[2, 0], sy)                   # Rotation about Y
            psi = 0                                                          # Rotation about Z

        return float(np.degrees(psi)), float(np.degrees(theta)), float(np.degrees(phi))

    @staticmethod
    def is_numerical(value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def rotation_matrix(axis, theta):
        """
        Returns the rotation matrix for a rotation about a given axis by an angle theta.
        """
        axis = np.asarray(axis)
        norm = np.linalg.norm(axis)
        if norm == 0:
            raise ValueError("Cannot rotate around zero vector")
        axis = axis / norm  # Ensure it's a unit vector
        u_x, u_y, u_z = axis
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        one_minus_cos_theta = 1 - cos_theta
        # Skew-symmetric matrix K
        K = np.array([[0, -u_z, u_y], [u_z, 0, -u_x], [-u_y, u_x, 0]])
        # Rotation matrix using Rodrigues' formula
        R = np.eye(3) + sin_theta * K + one_minus_cos_theta * np.dot(K, K)
        return R

# RegShape handling ===============================================
@dataclass
class RegShape:
    P1X: float = 0.0
    P1Y: float = 0.0
    P1Z: float = 0.0

@dataclass
class Circle(RegShape):
    PNX: float = 0.0
    PNY: float = 0.0
    PNZ: float = 0.0
    RAD: float = 0.0
    SMOOTH: float = 0.0
    CHECK: int = 0

@dataclass
class Slot(RegShape):
    P2X: float = 0.0
    P2Y: float = 0.0
    P2Z: float = 0.0
    PNX: float = 0.0
    PNY: float = 0.0
    PNZ: float = 0.0
    RAD: float = 0.0
    CHECK: int = 0

@dataclass
class Rectangle(RegShape):
    P2X: float = 0.0
    P2Y: float = 0.0
    P2Z: float = 0.0
    P3X: float = 0.0
    P3Y: float = 0.0
    P3Z: float = 0.0
    RAD: float = 0.0
    CHECK: int = 0

@dataclass
class Hexagon(RegShape):
    P2X: float = 0.0
    P2Y: float = 0.0
    P2Z: float = 0.0
    PNX: float = 0.0
    PNY: float = 0.0
    PNZ: float = 0.0
    RAD: float = 0.0
    CHECK: int = 0

@dataclass
class Keyhole(RegShape):
    P2X: float = 0.0
    P2Y: float = 0.0
    P2Z: float = 0.0
    PNX: float = 0.0
    PNY: float = 0.0
    PNZ: float = 0.0
    RAD: float = 0.0
    RAD2: float = 0.0
    CHECK: int = 0

@dataclass
class Position:
    X: float = 0.0
    Y: float = 0.0
    Z: float = 0.0

class ShapeParser(BaseParser):
    # ... Existing code from your ShapeParser class ...
    # Ensure that methods that can be reused are defined in BaseParser

    def __init__(self, operator: ULPythonUploadOperator, uploader: 'PrimaXmlUploader', regshape_patterns, shapes):
        super().__init__()
        self.operator = operator
        self.regshape_patterns = regshape_patterns
        self.shapes = shapes
        self.uploader = uploader  # Access PrimaXmlUploader instance here
        # Initialize shape objects
        self.Circle = Circle()
        self.Slot = Slot()
        self.Rectangle = Rectangle()
        self.Hexagon = Hexagon()
        self.Keyhole = Keyhole()
        self.regshapeApproachPosition = Position()
        self.regshapeLeadinPosition = Position()
        self.regshapeRetractPosition = Position()
        # Initialize flags and variables
        self.LaserOnType = ''
        self.LaserOnTechnicalParamType = 0
        self.LaserOnPiercingType = 0
        self.LocalFeed = 0
        self.regshapeRetractFeedrate = 0
        self.approachLeadinOnly = False
        self.regShapeG1 = False
        self.regShapeApproach = False
        self.regShapeFlyOff = False
        self.regShapeWorkOn = False
        self.regShapeFlyOn = False
        self.regShapeWorkOff = False
        self.regShapeRetract = False
        self.regShapeMotion = None
        self.regShapeBeforeEventRegShape = None

    def parse_regshape(self, operator: ULPythonUploadOperator, start_index: int, elements):
        logger = operator.GetLogOperator()
        regShapeMotion = None
        regShapeBeforeEvents = []
        regShapeAfterEvents = []
        index = start_index
        regshape_pattern = self.find_regshape_pattern(elements, index)
        if regshape_pattern:
            try:
                regShapeMotion, regShapeBeforeEvents, regShapeAfterEvents = self.process_regshape_pattern(operator, elements, regshape_pattern, index)
                index += len(regshape_pattern)
                # Reset class flags
                self._reset_flags()
                return index, regShapeMotion, regShapeBeforeEvents, regShapeAfterEvents
            except Exception as e:
                logger.LogError(f"Error processing regshape pattern: {e}")
                return start_index, None, [], []
        else:
            return start_index, None, [], []

    def _reset_flags(self):
        self.approachLeadinOnly = False
        self.regShapeG1 = False
        self.regShapeApproach = False
        self.regShapeFlyOff = False
        self.regShapeWorkOn = False
        self.regShapeFlyOn = False
        self.regShapeWorkOff = False
        self.regShapeRetract = False

    def process_regshape_pattern(self, operator: ULPythonUploadOperator, elements, regshape_pattern, start_index):

        regShapeMotion: ULPythonMotion = None
        regShapeBeforeEvents: list[ULPythonEvent] = []
        regShapeAfterEvents: list[ULPythonEvent] = []

        info = self.extract_regshape_information(elements, regshape_pattern, start_index)

        for tag, attributes in info.items():
            if tag == "G01":
                self.regShapeG1 = True
                self.regshapeApproachPosition.X = float(attributes["X"]) / 1000
                self.regshapeApproachPosition.Y = float(attributes["Y"]) / 1000
                self.regshapeApproachPosition.Z = float(attributes["Z"]) / 1000
                if attributes.get("LocalFeed"):
                    self.LocalFeed = float(attributes["LocalFeed"]) / 60000
            elif tag == "APPROACH":
                self.regShapeApproach = True
                self.regshapeLeadinPosition.X = float(attributes["X"]) / 1000
                self.regshapeLeadinPosition.Y = float(attributes["Y"]) / 1000
                self.regshapeLeadinPosition.Z = float(attributes["Z"]) / 1000
            elif tag == "FLY_ON":
                self.regShapeFlyOn = True
            elif tag == "WORK_ON":
                self.regShapeWorkOn = True
                self.LaserOnType = tag
                self.LaserOnTechnicalParamType = int(attributes["LaserLine"])
                self.LaserOnPiercingType = int(attributes["PiercingType"])
            elif tag == "FLY_OFF":
                self.regShapeFlyOff = True
            elif tag == "WORK_OFF":
                self.regShapeWorkOff = True
            elif tag == "FEED":
                self.regshapeRetractFeedrate = int(attributes["Value"])
            elif tag == "RETRACT":
                self.regShapeRetract = True
                self.regshapeRetractPosition.X = float(attributes["X"]) / 1000
                self.regshapeRetractPosition.Y = float(attributes["Y"]) / 1000
                self.regshapeRetractPosition.Z = float(attributes["Z"]) / 1000

        # If there is no APPROACH in the pattern, G1 becomes the lead-in instead of the approach
        if self.regShapeG1 and not self.regShapeApproach:
            self.approachLeadinOnly = True
            self.regshapeLeadinPosition = Position(
                X=self.regshapeApproachPosition.X,
                Y=self.regshapeApproachPosition.Y,
                Z=self.regshapeApproachPosition.Z
            )

        shape_parsers = {
            "HOLE": self.parse_circle_event,
            "SLOT": self.parse_slot_event,
            "RECT": self.parse_rectangle_event,
            "POLY": self.parse_hexagon_event,
            "KEYHOLE": self.parse_keyhole_event
        }

        # Parse the actual regshapes
        for tag, attributes in info.items():
            if tag in shape_parsers:
                regShapeMotion, regShapeBeforeEvents, regShapeAfterEvents = shape_parsers[tag](self.operator, attributes)

        if regShapeMotion:
            return regShapeMotion, regShapeBeforeEvents, regShapeAfterEvents
            
        # # Reset regshape items
        # regShapeMotion = None
        # regShapeBeforeEvents.clear()
        # regShapeAfterEvents.clear()

        return

    def find_regshape_pattern(self, elements, start_index):
        """
        Find a matching pattern from the base patterns starting at a specific index.

        :param elements: List of XML elements
        :param start_index: Index to start checking for patterns
        :return: Matching pattern if found, None otherwise
        """
        for regshape_pattern in self.regshape_patterns:
            if self.match_regshape_pattern(elements, start_index, regshape_pattern):
                return regshape_pattern
        return None

    def match_regshape_pattern(self, elements, start_index, pattern):
        """
        Check if a pattern matches the elements starting from a specific index.

        :param elements: List of XML elements
        :param start_index: Index to start checking the pattern
        :param pattern: Pattern to match
        :return: True if the pattern matches, False otherwise
        """
        if start_index + len(pattern) > len(elements):
            return False
        for i, tag in enumerate(pattern):
            if tag == "{SHAPE}":
                if elements[start_index + i].tag not in self.shapes:
                    return False
            elif elements[start_index + i].tag != tag:
                return False
        return True

    def extract_regshape_information(self, elements, pattern, start_index):
        """
        Extract information from elements matching a specific pattern.

        :param elements: List of XML elements
        :param pattern: Pattern to extract information from
        :param start_index: Index to start extraction
        :return: Dictionary containing extracted information
        """
        info = {}
        for i, tag in enumerate(pattern):
            element = elements[start_index + i]
            resolved_tag = element.tag if tag == "{SHAPE}" else tag
            info[resolved_tag] = element.attrib
        return info

    def parse_circle_event(self, operator: ULPythonUploadOperator, attributes):
        self.Circle.P1X = float(attributes["Xc"]) / 1000
        self.Circle.P1Y = float(attributes["Yc"]) / 1000
        self.Circle.P1Z = float(attributes["Zc"]) / 1000
        self.Circle.PNX = float(attributes["Xn"]) / 1000
        self.Circle.PNY = float(attributes["Yn"]) / 1000
        self.Circle.PNZ = float(attributes["Zn"]) / 1000
        self.Circle.RAD = float(attributes["Radius"]) / 1000
        self.Circle.SMOOTH = float(attributes["Smooth"])
        self.Circle.CHECK = int(attributes.get("Check", "0"))

        reference_x = self.Circle.P1X
        reference_y = self.Circle.P1Y
        reference_z = self.Circle.P1Z

        reference_vector_z = np.array([
            self.Circle.PNX - self.Circle.P1X,
            self.Circle.PNY - self.Circle.P1Y,
            self.Circle.PNZ - self.Circle.P1Z,
        ])
        reference_vector_z = self.normalize_vector(reference_vector_z)

        # Method from Prima C++ technology
        bRot = False
        if (self.Circle.PNX - self.Circle.P1X) < 0.000001 and (
            self.Circle.PNY - self.Circle.P1Y
        ) < 0.000001:
            xp = self.Circle.P1X + 1
            yp = self.Circle.P1Y
            zp = self.Circle.P1Z
        else:
            xp = self.Circle.P1X + (self.Circle.PNX - self.Circle.P1X)
            yp = self.Circle.P1Y + (self.Circle.PNY - self.Circle.P1Y)
            zp = self.Circle.P1Z
            bRot = True
        worldZ = np.array([0, 0, 1])
        zRotM = np.identity(3)
        if bRot:
            zRotM = self.rotation_matrix(worldZ, -0.5 * math.pi)
        pC = np.array([self.Circle.P1X, self.Circle.P1Y, self.Circle.P1Z])
        pT = np.array([xp, yp, zp])
        tAxis = pT - pC
        tAxis = self.normalize_vector(tAxis)
        tAxis = np.dot(zRotM, tAxis)
        reference_vector_x = self.normalize_vector(tAxis)
        reference_vector_y = np.cross(reference_vector_z, reference_vector_x)
        reference_vector_y = self.normalize_vector(reference_vector_y)

        # Calculate distances
        leadinPoint = np.array([
            self.regshapeLeadinPosition.X,
            self.regshapeLeadinPosition.Y,
            self.regshapeLeadinPosition.Z,
        ])
        centerPoint = np.array([reference_x, reference_y, reference_z])
        pointToPlane_Vector = leadinPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        projectedPoint = leadinPoint - distance * reference_vector_z
        piercingDistance = round(np.linalg.norm(leadinPoint - projectedPoint), 4)
        leadinDistance = round(
            self.Circle.RAD - np.linalg.norm(projectedPoint - centerPoint),
            4,
        )

        approachDistance = 0
        if not self.approachLeadinOnly:
            approachPoint = np.array([
                self.regshapeApproachPosition.X,
                self.regshapeApproachPosition.Y,
                self.regshapeApproachPosition.Z,
            ])
            approachDistance = round(
                np.linalg.norm(approachPoint - projectedPoint), 4
            )

        retractDistance = 0
        retractPoint = np.array([
            self.regshapeRetractPosition.X,
            self.regshapeRetractPosition.Y,
            self.regshapeRetractPosition.Z,
        ])
        pointToPlane_Vector = retractPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        projectedPoint = retractPoint - distance * reference_vector_z
        retractDistance = round(
            np.linalg.norm(retractPoint - projectedPoint), 4
        )

        regShapePathRef = str(tuple(map(float,reference_vector_x))) + ', '+ str(tuple(map(float,reference_vector_y))) + ', ' + str(tuple(map(float,reference_vector_z)))

        self.regShapeBeforeEventRegShape = PrimaXmlUploader.create_event_with_attributes(
            operator,
            "CIRCLE",
            TPINSERTPOS_INSERTBEFORE,
            {
                "P1X": {"Value": self.Circle.P1X, "Type": float},
                "P1Y": {"Value": self.Circle.P1Y, "Type": float},
                "P1Z": {"Value": self.Circle.P1Z, "Type": float},
                "PNX": {"Value": self.Circle.PNX, "Type": float},
                "PNY": {"Value": self.Circle.PNY, "Type": float},
                "PNZ": {"Value": self.Circle.PNZ, "Type": float},
                "RAD": {"Value": self.Circle.RAD, "Type": float},
                "SMOOTH": {"Value": self.Circle.SMOOTH, "Type": float},
                "CHECK": {"Value": self.Circle.CHECK, "Type": int},
                "RegShapePathRefMatrix": {"Value": regShapePathRef, "Type": str},
            },
        )

        # Create Reference Motion and Approach and Retract events
        return self.createRegshapeApprRetrEvents(
            operator,
            approachDistance,
            piercingDistance,
            leadinDistance,
            retractDistance,
            reference_vector_x,
            reference_vector_y,
            reference_vector_z,
            reference_x,
            reference_y,
            reference_z
        )

    def parse_slot_event(self, operator: ULPythonUploadOperator, attributes):
        self.Slot.P1X = float(attributes["Xc"]) / 1000
        self.Slot.P1Y = float(attributes["Yc"]) / 1000
        self.Slot.P1Z = float(attributes["Zc"]) / 1000
        self.Slot.P2X = float(attributes["Xc2"]) / 1000
        self.Slot.P2Y = float(attributes["Yc2"]) / 1000
        self.Slot.P2Z = float(attributes["Zc2"]) / 1000
        self.Slot.PNX = float(attributes["Xn"]) / 1000
        self.Slot.PNY = float(attributes["Yn"]) / 1000
        self.Slot.PNZ = float(attributes["Zn"]) / 1000
        self.Slot.RAD = float(attributes["Radius"]) / 1000
        self.Slot.CHECK = int(attributes.get("Check", "0"))

        reference_x = self.Slot.P1X + (self.Slot.P2X - self.Slot.P1X) / 2
        reference_y = self.Slot.P1Y + (self.Slot.P2Y - self.Slot.P1Y) / 2
        reference_z = self.Slot.P1Z + (self.Slot.P2Z - self.Slot.P1Z) / 2

        reference_vector_z = np.array([
                (self.Slot.PNX - self.Slot.P2X) * 1000,
                (self.Slot.PNY - self.Slot.P2Y) * 1000,
                (self.Slot.PNZ - self.Slot.P2Z) * 1000,
        ])
        reference_vector_z = self.normalize_vector(reference_vector_z)
        reference_vector_x = np.array([
                (self.Slot.P1X - self.Slot.P2X) * 1000,
                (self.Slot.P1Y - self.Slot.P2Y) * 1000,
                (self.Slot.P1Z - self.Slot.P2Z) * 1000,
        ])
        reference_vector_x = self.normalize_vector(reference_vector_x)
        reference_vector_y = np.cross(reference_vector_z, reference_vector_x)
        reference_vector_y = self.normalize_vector(reference_vector_y)
        # Z and X vectors are not neccessarily orthogonal. Therefore the X vector needs to be recalculated
        reference_vector_x = np.cross(reference_vector_y, reference_vector_z)
        reference_vector_x = self.normalize_vector(reference_vector_x)

        # Calculate the piercing distance from the leading point to the regshape's plane
        leadinPoint = np.array([
                self.regshapeLeadinPosition.X,
                self.regshapeLeadinPosition.Y,
                self.regshapeLeadinPosition.Z,
        ])
        centerPoint = np.array([reference_x, reference_y, reference_z])
        pointToPlane_Vector = leadinPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = leadinPoint - distance * reference_vector_z
        piercingDistance = round(
            np.abs(np.linalg.norm(leadinPoint - projectedPoint)), 4
        )
        # calculate leadin distance
        pointToPlane_Vector = projectedPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_y)
        projectedPointXZ = projectedPoint - distance * reference_vector_y
        leadinDistance = round(
            np.abs(self.Slot.RAD - np.abs((np.linalg.norm(projectedPoint - projectedPointXZ)))),4,
        )

        approachDistance = 0
        if not self.approachLeadinOnly:
            # Calculate the APPROACH distance from the leading point to the regshape's plane
            approachPoint = np.array([
                    self.regshapeApproachPosition.X,
                    self.regshapeApproachPosition.Y,
                    self.regshapeApproachPosition.Z,
            ])
            approachDistance = round(
                np.abs(np.linalg.norm(approachPoint - projectedPoint)), 4
            )

        retractDistance = 0
        retractPoint = np.array(
            [
                self.regshapeRetractPosition.X,
                self.regshapeRetractPosition.Y,
                self.regshapeRetractPosition.Z,
            ]
        )
        pointToPlane_Vector = retractPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = retractPoint - distance * reference_vector_z
        retractDistance = round(
            np.abs(np.linalg.norm(retractPoint - projectedPoint)), 4
        )

        regShapePathRef = str(tuple(map(float,reference_vector_x))) + ', '+ str(tuple(map(float,reference_vector_y))) + ', ' + str(tuple(map(float,reference_vector_z)))

        self.regShapeBeforeEventRegShape = PrimaXmlUploader.create_event_with_attributes(
            operator,
            "SLOT",
            TPINSERTPOS_INSERTBEFORE,
            {
                "P1X": {"Value": self.Slot.P1X, "Type": float},
                "P1Y": {"Value": self.Slot.P1Y, "Type": float},
                "P1Z": {"Value": self.Slot.P1Z, "Type": float},
                "P2X": {"Value": self.Slot.P2X, "Type": float},
                "P2Y": {"Value": self.Slot.P2Y, "Type": float},
                "P2Z": {"Value": self.Slot.P2Z, "Type": float},
                "PNX": {"Value": self.Slot.PNX, "Type": float},
                "PNY": {"Value": self.Slot.PNY, "Type": float},
                "PNZ": {"Value": self.Slot.PNZ, "Type": float},
                "RAD": {"Value": self.Slot.RAD, "Type": float},
                "CHECK": {"Value": self.Slot.CHECK, "Type": int},
                "RegShapePathRefMatrix": {"Value": regShapePathRef, "Type": str},
            },
        )

        # Create Reference Motion and Approach and Retract events
        return self.createRegshapeApprRetrEvents(
            operator,
            approachDistance,
            piercingDistance,
            leadinDistance,
            retractDistance,
            reference_vector_x,
            reference_vector_y,
            reference_vector_z,
            reference_x,
            reference_y,
            reference_z
        )

    def parse_rectangle_event(self, operator: ULPythonUploadOperator, attributes):
        self.Rectangle.P1X = float(attributes["Xc"]) / 1000
        self.Rectangle.P1Y = float(attributes["Yc"]) / 1000
        self.Rectangle.P1Z = float(attributes["Zc"]) / 1000
        self.Rectangle.P2X = float(attributes["Xv"]) / 1000
        self.Rectangle.P2Y = float(attributes["Yv"]) / 1000
        self.Rectangle.P2Z = float(attributes["Zv"]) / 1000
        self.Rectangle.P3X = float(attributes["Xs"]) / 1000
        self.Rectangle.P3Y = float(attributes["Ys"]) / 1000
        self.Rectangle.P3Z = float(attributes["Zs"]) / 1000
        self.Rectangle.RAD = float(attributes["Radius"]) / 1000
        self.Rectangle.CHECK = int(attributes.get("Check", "0"))

        reference_x = self.Rectangle.P1X
        reference_y = self.Rectangle.P1Y
        reference_z = self.Rectangle.P1Z

        reference_vector_y = np.array([
                (self.Rectangle.P2X - self.Rectangle.P3X) * 1000,
                (self.Rectangle.P2Y - self.Rectangle.P3Y) * 1000,
                (self.Rectangle.P2Z - self.Rectangle.P3Z) * 1000,
        ])
        reference_vector_y = self.normalize_vector(reference_vector_y)
        reference_vector_x = np.array([
                (self.Rectangle.P3X - self.Rectangle.P1X) * 1000,
                (self.Rectangle.P3Y - self.Rectangle.P1Y) * 1000,
                (self.Rectangle.P3Z - self.Rectangle.P1Z) * 1000,
        ])
        reference_vector_x = self.normalize_vector(reference_vector_x)
        reference_vector_z = np.cross(reference_vector_x, reference_vector_y)
        reference_vector_z = self.normalize_vector(reference_vector_z)
        # Z and X vectors are not neccessarily orthogonal. Therefore the X vector needs to be recalculated
        reference_vector_x = np.cross(reference_vector_y, reference_vector_z)
        reference_vector_x = self.normalize_vector(reference_vector_x)

        # Calculate the piercing distance from the leading point to the regshape's plane
        leadinPoint = np.array([
                self.regshapeLeadinPosition.X,
                self.regshapeLeadinPosition.Y,
                self.regshapeLeadinPosition.Z,
        ])
        centerPoint = np.array([reference_x, reference_y, reference_z])
        pointToPlane_Vector = leadinPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = leadinPoint - distance * reference_vector_z
        piercingDistance = round(
            np.abs(np.linalg.norm(leadinPoint - projectedPoint)), 4
        )
        # calculate leadin distance
        pointToPlane_Vector = projectedPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_y)
        projectedPointXZ = projectedPoint - distance * reference_vector_y
        leadinDistance = round(
            np.abs(self.Rectangle.RAD - np.abs((np.linalg.norm(projectedPoint - projectedPointXZ)))),4,
        )

        approachDistance = 0
        if not self.approachLeadinOnly:
            # Calculate the APPROACH distance from the leading point to the regshape's plane
            approachPoint = np.array([
                    self.regshapeApproachPosition.X,
                    self.regshapeApproachPosition.Y,
                    self.regshapeApproachPosition.Z,
            ])
            approachDistance = round(
                np.abs(np.linalg.norm(approachPoint - projectedPoint)), 4
            )

        retractDistance = 0
        retractPoint = np.array([
                self.regshapeRetractPosition.X,
                self.regshapeRetractPosition.Y,
                self.regshapeRetractPosition.Z,
        ])
        pointToPlane_Vector = retractPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = retractPoint - distance * reference_vector_z
        retractDistance = round(
            np.abs(np.linalg.norm(retractPoint - projectedPoint)), 4
        )

        regShapePathRef = str(tuple(map(float,reference_vector_x))) + ', '+ str(tuple(map(float,reference_vector_y))) + ', ' + str(tuple(map(float,reference_vector_z)))

        self.regShapeBeforeEventRegShape = PrimaXmlUploader.create_event_with_attributes(
            operator,
            "RECTANGLE",
            TPINSERTPOS_INSERTBEFORE,
            {
                "P1X": {"Value": self.Rectangle.P1X, "Type": float},
                "P1Y": {"Value": self.Rectangle.P1Y, "Type": float},
                "P1Z": {"Value": self.Rectangle.P1Z, "Type": float},
                "P2X": {"Value": self.Rectangle.P2X, "Type": float},
                "P2Y": {"Value": self.Rectangle.P2Y, "Type": float},
                "P2Z": {"Value": self.Rectangle.P2Z, "Type": float},
                "P3X": {"Value": self.Rectangle.P3X, "Type": float},
                "P3Y": {"Value": self.Rectangle.P3Y, "Type": float},
                "P3Z": {"Value": self.Rectangle.P3Z, "Type": float},
                "RAD": {"Value": self.Rectangle.RAD, "Type": float},
                "CHECK": {"Value": self.Rectangle.CHECK, "Type": int},
                "RegShapePathRefMatrix": {"Value": regShapePathRef, "Type": str},
            },
        )
        
        # Create Reference Motion and Approach and Retract events
        return self.createRegshapeApprRetrEvents(
            operator,
            approachDistance,
            piercingDistance,
            leadinDistance,
            retractDistance,
            reference_vector_x,
            reference_vector_y,
            reference_vector_z,
            reference_x,
            reference_y,
            reference_z
        )

    def parse_hexagon_event(self, operator: ULPythonUploadOperator, attributes):
        self.Hexagon.P1X = float(attributes["Xc"]) / 1000
        self.Hexagon.P1Y = float(attributes["Yc"]) / 1000
        self.Hexagon.P1Z = float(attributes["Zc"]) / 1000
        self.Hexagon.P2X = float(attributes["Xv"]) / 1000
        self.Hexagon.P2Y = float(attributes["Yv"]) / 1000
        self.Hexagon.P2Z = float(attributes["Zv"]) / 1000
        self.Hexagon.PNX = float(attributes["Xn"]) / 1000
        self.Hexagon.PNY = float(attributes["Yn"]) / 1000
        self.Hexagon.PNZ = float(attributes["Zn"]) / 1000
        self.Hexagon.RAD = float(attributes["Radius"]) / 1000
        self.Hexagon.CHECK = int(attributes.get("Check", "0"))

        reference_x = self.Hexagon.P1X
        reference_y = self.Hexagon.P1Y
        reference_z = self.Hexagon.P1Z

        reference_vector_y = np.array([
                (self.Hexagon.P2X - self.Hexagon.P1X) * 1000,
                (self.Hexagon.P2Y - self.Hexagon.P1Y) * 1000,
                (self.Hexagon.P2Z - self.Hexagon.P1Z) * 1000,
        ])
        reference_vector_y = self.normalize_vector(reference_vector_y)
        reference_vector_z = np.array([
                (self.Hexagon.PNX - self.Hexagon.P2X) * 1000,
                (self.Hexagon.PNY - self.Hexagon.P2Y) * 1000,
                (self.Hexagon.PNZ - self.Hexagon.P2Z) * 1000,
        ])
        reference_vector_z = self.normalize_vector(reference_vector_z)
        reference_vector_x = np.cross(reference_vector_y, reference_vector_z)
        reference_vector_x = self.normalize_vector(reference_vector_x)

        # Calculate the piercing distance from the leading point to the regshape's plane
        leadinPoint = np.array([
                self.regshapeLeadinPosition.X,
                self.regshapeLeadinPosition.Y,
                self.regshapeLeadinPosition.Z,
        ])
        centerPoint = np.array([reference_x, reference_y, reference_z])
        pointToPlane_Vector = leadinPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = leadinPoint - distance * reference_vector_z
        piercingDistance = round(
            np.abs(np.linalg.norm(leadinPoint - projectedPoint)), 4
        )
        # calculate leadin distance
        pointToPlane_Vector = projectedPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_y)
        projectedPointXZ = projectedPoint - distance * reference_vector_y
        leadinDistance = round(
            (self.Hexagon.RAD - np.abs((np.linalg.norm(projectedPoint - projectedPointXZ)))),4,
        )

        approachDistance = 0
        if not self.approachLeadinOnly:
            # Calculate the APPROACH distance from the leading point to the regshape's plane
            approachPoint = np.array([
                    self.regshapeApproachPosition.X,
                    self.regshapeApproachPosition.Y,
                    self.regshapeApproachPosition.Z,
            ])
            approachDistance = round(
                np.abs(np.linalg.norm(approachPoint - projectedPoint)), 4
            )

        retractDistance = 0
        retractPoint = np.array([
                self.regshapeRetractPosition.X,
                self.regshapeRetractPosition.Y,
                self.regshapeRetractPosition.Z,
        ])
        pointToPlane_Vector = retractPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = retractPoint - distance * reference_vector_z
        retractDistance = round(
            np.abs(np.linalg.norm(retractPoint - projectedPoint)), 4
        )

        regShapePathRef = str(tuple(map(float,reference_vector_x))) + ', '+ str(tuple(map(float,reference_vector_y))) + ', ' + str(tuple(map(float,reference_vector_z)))

        self.regShapeBeforeEventRegShape = PrimaXmlUploader.create_event_with_attributes(
            operator,
            "HEXAGON",
            TPINSERTPOS_INSERTBEFORE,
            {
                "P1X": {"Value": self.Hexagon.P1X, "Type": float},
                "P1Y": {"Value": self.Hexagon.P1Y, "Type": float},
                "P1Z": {"Value": self.Hexagon.P1Z, "Type": float},
                "P2X": {"Value": self.Hexagon.P2X, "Type": float},
                "P2Y": {"Value": self.Hexagon.P2Y, "Type": float},
                "P2Z": {"Value": self.Hexagon.P2Z, "Type": float},
                "PNX": {"Value": self.Hexagon.PNX, "Type": float},
                "PNY": {"Value": self.Hexagon.PNY, "Type": float},
                "PNZ": {"Value": self.Hexagon.PNZ, "Type": float},
                "RAD": {"Value": self.Hexagon.RAD, "Type": float},
                "CHECK": {"Value": self.Hexagon.CHECK, "Type": int},
                "RegShapePathRefMatrix": {"Value": regShapePathRef, "Type": str},
            },
        )

        # Create Reference Motion and Approach and Retract events
        return self.createRegshapeApprRetrEvents(
            operator,
            approachDistance,
            piercingDistance,
            leadinDistance,
            retractDistance,
            reference_vector_x,
            reference_vector_y,
            reference_vector_z,
            reference_x,
            reference_y,
            reference_z
        )

    def parse_keyhole_event(self, operator: ULPythonUploadOperator, attributes):
        self.Keyhole.P1X = float(attributes["Xc"]) / 1000
        self.Keyhole.P1Y = float(attributes["Yc"]) / 1000
        self.Keyhole.P1Z = float(attributes["Zc"]) / 1000
        self.Keyhole.P2X = float(attributes["Xc2"]) / 1000
        self.Keyhole.P2Y = float(attributes["Yc2"]) / 1000
        self.Keyhole.P2Z = float(attributes["Zc2"]) / 1000
        self.Keyhole.PNX = float(attributes["Xn"]) / 1000
        self.Keyhole.PNY = float(attributes["Yn"]) / 1000
        self.Keyhole.PNZ = float(attributes["Zn"]) / 1000
        self.Keyhole.RAD = float(attributes["Radius"]) / 1000
        self.Keyhole.RAD2 = float(attributes["Radius2"]) / 1000
        self.Keyhole.CHECK = int(attributes.get("Check", "0"))

        reference_x = self.Keyhole.P1X
        reference_y = self.Keyhole.P1Y
        reference_z = self.Keyhole.P1Z

        reference_vector_y = np.array([
                (self.Keyhole.P2X - self.Keyhole.P1X) * 1000,
                (self.Keyhole.P2Y - self.Keyhole.P1Y) * 1000,
                (self.Keyhole.P2Z - self.Keyhole.P1Z) * 1000,
        ])
        reference_vector_y = self.normalize_vector(reference_vector_y)
        reference_vector_z = np.array([
                (self.Keyhole.PNX - self.Keyhole.P2X) * 1000,
                (self.Keyhole.PNY - self.Keyhole.P2Y) * 1000,
                (self.Keyhole.PNZ - self.Keyhole.P2Z) * 1000,
        ])
        reference_vector_z = self.normalize_vector(reference_vector_z)
        reference_vector_x = np.cross(reference_vector_y, reference_vector_z)
        reference_vector_x = self.normalize_vector(reference_vector_x)

        # Calculate the piercing distance from the leading point to the regshape's plane
        leadinPoint = np.array([
                self.regshapeLeadinPosition.X,
                self.regshapeLeadinPosition.Y,
                self.regshapeLeadinPosition.Z,
        ])
        centerPoint = np.array([reference_x, reference_y, reference_z])
        pointToPlane_Vector = leadinPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = leadinPoint - distance * reference_vector_z
        piercingDistance = round(
            np.abs(np.linalg.norm(leadinPoint - projectedPoint)), 4
        )
        # calculate leadin distance
        pointToPlane_Vector = projectedPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_y)
        projectedPointXZ = projectedPoint - distance * reference_vector_y
        leadinDistance = round(
            (self.Keyhole.RAD - np.abs((np.linalg.norm(projectedPoint - projectedPointXZ)))),4,
        )

        approachDistance = 0
        if not self.approachLeadinOnly:
            # Calculate the APPROACH distance from the leading point to the regshape's plane
            approachPoint = np.array([
                    self.regshapeApproachPosition.X,
                    self.regshapeApproachPosition.Y,
                    self.regshapeApproachPosition.Z,
            ])
            approachDistance = round(
                np.abs(np.linalg.norm(approachPoint - projectedPoint)), 4
            )

        retractDistance = 0
        retractPoint = np.array([
                self.regshapeRetractPosition.X,
                self.regshapeRetractPosition.Y,
                self.regshapeRetractPosition.Z,
        ])
        pointToPlane_Vector = retractPoint - centerPoint
        distance = np.dot(pointToPlane_Vector, reference_vector_z)
        # Calculate leadin point projected onto regshape's plane
        projectedPoint = retractPoint - distance * reference_vector_z
        retractDistance = round(
            np.abs(np.linalg.norm(retractPoint - projectedPoint)), 4
        )

        regShapePathRef = str(tuple(map(float,reference_vector_x))) + ', '+ str(tuple(map(float,reference_vector_y))) + ', ' + str(tuple(map(float,reference_vector_z)))

        self.regShapeBeforeEventRegShape = PrimaXmlUploader.create_event_with_attributes(
            operator,
            "KEYHOLE",
            TPINSERTPOS_INSERTBEFORE,
            {
                "P1X": {"Value": self.Keyhole.P1X, "Type": float},
                "P1Y": {"Value": self.Keyhole.P1Y, "Type": float},
                "P1Z": {"Value": self.Keyhole.P1Z, "Type": float},
                "P2X": {"Value": self.Keyhole.P2X, "Type": float},
                "P2Y": {"Value": self.Keyhole.P2Y, "Type": float},
                "P2Z": {"Value": self.Keyhole.P2Z, "Type": float},
                "PNX": {"Value": self.Keyhole.PNX, "Type": float},
                "PNY": {"Value": self.Keyhole.PNY, "Type": float},
                "PNZ": {"Value": self.Keyhole.PNZ, "Type": float},
                "RAD1": {"Value": self.Keyhole.RAD, "Type": float},
                "RAD2": {"Value": self.Keyhole.RAD2, "Type": float},
                "CHECK": {"Value": self.Keyhole.CHECK, "Type": int},
                "RegShapePathRefMatrix": {"Value": regShapePathRef, "Type": str},
            },
        )

        # Create Reference Motion and Approach and Retract events
        return self.createRegshapeApprRetrEvents(
            operator,
            approachDistance,
            piercingDistance,
            leadinDistance,
            retractDistance,
            reference_vector_x,
            reference_vector_y,
            reference_vector_z,
            reference_x,
            reference_y,
            reference_z
        )

    def create_reference_motion(
        self,
        operator: ULPythonUploadOperator,
        ref_vec_x,
        ref_vec_y,
        ref_vec_z,
        ref_x,
        ref_y,
        ref_z,
    ):
        ul_reference_motion: ULPythonMotion = None
        ul_reference_position: ULPythonPosition = None
        ul_reference_position = operator.CreateEmptyPosition()
        ul_reference_position.SetProcessType(ProcessType.ProcessPoint)
        ul_reference_position.SetTargetType(TargetType.Cartesian)
        ul_reference_position.SetXYZ((ref_x, ref_y, ref_z))

        reference_matrix = np.column_stack((ref_vec_x, ref_vec_y, ref_vec_z))
        rot_x, rot_y, rot_z = self.extract_euler_angles(reference_matrix)
        rsOri = [rot_z, rot_y, rot_x]

        # Calculate the difference between self.current_Orientation and rsOri
        difference = [curr - rs for curr, rs in zip(self.uploader.current_Orientation, rsOri)]

        # Check if any absolute value in the list is smaller than 0.01
        is_any_abs_greater = any(abs(x) > 0.001 for x in difference)

        # Set ref element orientation to match the one of the previous move, usually the leadin point if the orientation differs from the ori of the regshape
        if is_any_abs_greater:
            ul_reference_position.SetOrientation(tuple(self.uploader.current_Orientation))
        else:
            ul_reference_position.SetOrientation(tuple(rsOri))

        ul_reference_motion = operator.CreateEmptyMotion()
        ul_reference_motion.SetMotionType(MotionType.Linear)
        ul_reference_motion.SetPosition(ul_reference_position)
        return ul_reference_motion

    def createRegshapeApprRetrEvents(self, operator: ULPythonUploadOperator, 
            approach_distance, piercing_distance, leadin_distance, retract_distance,
            ref_vector_x, ref_vector_y, ref_vector_z,
            ref_x, ref_y, ref_z):

        regShapeMotion: ULPythonMotion = None
        regShapeBeforeEvents: list[ULPythonEvent] = []
        regShapeAfterEvents: list[ULPythonEvent] = []

        if self.regShapeG1 and self.regShapeApproach:
            # self.regShapeBeforeEventApproach = PrimaXmlUploader.create_event_with_attributes(
            regShapeBeforeEvents.append(PrimaXmlUploader.create_event_with_attributes(
                operator,
                "RegshapeApproach",
                TPINSERTPOS_INSERTBEFORE,
                {
                    "FirstSafetyDistance": {"Value": approach_distance, "Type": float},
                    "SecondSafetyDistance": {"Value": 0, "Type": float},
                    "PiercingDistance": {"Value": piercing_distance, "Type": float},
                    "LeadInDistance": {"Value": leadin_distance, "Type": float},
                    "FirstSafetyFeedrate": {"Value": self.LocalFeed, "Type": float},
                    "SecondSafetyFeedrate": {"Value": 3.45, "Type": float},
                    "PiercingFeedrate": {"Value": 0.833333, "Type": float},
                    "LaserOnTechnicalParamType": {"Value": self.LaserOnTechnicalParamType, "Type": float},
                    "LaserOnPiercingType": {"Value": self.LaserOnPiercingType, "Type": float},
                },
            ))
        elif self.regShapeG1:
            regShapeBeforeEvents.append(PrimaXmlUploader.create_event_with_attributes(
                operator,
                "RegshapeApproachLeadin",
                TPINSERTPOS_INSERTBEFORE,
                {
                    "LeadInDistance": {"Value": leadin_distance, "Type": float},
                    "PiercingDistance": {"Value": piercing_distance, "Type": float},
                    "FirstSafetyFeedrate": {"Value": 3.45, "Type": float},
                },
            ))
        elif self.regShapeWorkOn:
            if self.regShapeFlyOff:
                regShapeBeforeEvents.append(PrimaXmlUploader.create_event_with_attributes(
                    operator,
                    "Accuracy",
                    TPINSERTPOS_INSERTBEFORE,
                    {
                        "Value": {"Value": 0.0, "Type": float},
                        "Criteria": {"Value": "Velocity", "Type": str},
                        "PathType": {"Value": "Contour", "Type": str},
                    },
                ))
            regShapeBeforeEvents.append(PrimaXmlUploader.handle_laser_on_event(
                operator, 
                self.LaserOnType, 
                self.LaserOnTechnicalParamType, 
                self.LaserOnPiercingType
            ))
            if self.regShapeFlyOn:
                regShapeBeforeEvents.append(PrimaXmlUploader.create_event_with_attributes(
                    operator,
                    "Accuracy",
                    TPINSERTPOS_INSERTBEFORE,
                    {
                        "Value": {"Value": 0.001234, "Type": float},
                        "Criteria": {"Value": "Distance", "Type": str},
                        "PathType": {"Value": "Contour", "Type": str},
                    },
                ))

        # Append actual regshape event
        regShapeBeforeEvents.append(self.regShapeBeforeEventRegShape)

        regShapeAfterEvents.append(PrimaXmlUploader.create_event_with_attributes(
            operator,
            "RegshapeRetractLeadout",
            TPINSERTPOS_INSERTAFTER,
            {
                "RetractDistance": {"Value": 0.0, "Type": float}, 
                "RetractFeedrate": {"Value": self.LocalFeed, "Type": float},
            },
        ))
        
        if self.regShapeRetract:
            regShapeAfterEvents.append(PrimaXmlUploader.create_event_with_attributes(
                operator,
                "RegshapeRetract",
                TPINSERTPOS_INSERTAFTER,
                {
                    "RetractDistance": {"Value": retract_distance, "Type": float},
                    "RetractFeedrate": {"Value": self.regshapeRetractFeedrate / 60000, "Type": float},
                },
            ))

        regShapeMotion = self.create_reference_motion(
            operator,
            ref_vector_x,
            ref_vector_y,
            ref_vector_z,
            ref_x,
            ref_y,
            ref_z,
        )

        return regShapeMotion, regShapeBeforeEvents, regShapeAfterEvents

#Main Prima XML uploader class
class PrimaXmlUploader(Uploader, BaseParser):
    def __init__(self):
        super().__init__()
        self._program_name = ''
        self._program_list = []
        self._headerCompleted = False
        self._opGroupSet = False
        self._operationSet = False
        self._text_event_list = []
        self._base_profile_list = []
        self._tool_profile_list = []
        self._all_joints_list = []
        self.tool_profile_default_index = 1
        self.base_profile_default_index = 1
        self.tool_profile_default = None
        self.base_profile_default = None
        self.uploadRefBaseFrame = ''
        self.base_profile_g113 = None
        # Store the last seen G113 attributes until we find a G114 to pair with
        self.last_g113_attrs = None
        self.base_profile_car_index = 0
        self.current_Orientation: list[float] = [0, 0, 0]
        self.clamp_base_name: str = ''
        self.events_before: list[ULPythonEvent] = []
        self.events_after: list[ULPythonEvent] = []
        self.xml_pattern_parser = None  # Will initialize in Initialize method
        self.shape_parser = None  # Will initialize in Initialize method
        # self.regshape_patterns = [
        #     ["FLY_OFF", "WORK_ON", "{SHAPE}", "WORK_OFF", "FEED", "FLY_ON", "RETRACT"],
        #     ["FLY_OFF", "WORK_ON", "{SHAPE}", "WORK_OFF"],
        #     ["WORK_ON", "{SHAPE}", "WORK_OFF", "FEED", "FLY_ON", "RETRACT"],
        #     ["WORK_ON", "{SHAPE}", "WORK_OFF"],
        # ]
        self.regshape_patterns = [
            ["FLY_OFF", "WORK_ON", "{SHAPE}", "WORK_OFF"],
            ["WORK_ON", "{SHAPE}", "WORK_OFF"],
            ["WORK_ON", "FLY_ON", "{SHAPE}", "WORK_OFF"],
        ]
        self.shapes = ["SLOT", "HOLE", "RECT", "POLY", "KEYHOLE"]
        self.lastCoordX = 0.0
        self.lastCoordY = 0.0
        self.lastCoordZ = 0.0
        self.lastCoordC = 0.0
        self.lastCoordA = 0.0
        self.lastCoordI = 0.0
        self.lastCoordJ = 0.0
        self.lastCoordK = 0.0
        self.lastMotionLinear = None
        self.ABZeroDeviation = 0.03

    def Initialize(self, operator: ULPythonUploadOperator):
        logger = operator.GetLogOperator()
        logger.LogDebug("PrimaXml Initialize called")

        controller = operator.GetController()
        self._base_profile_list = controller.GetBaseProfiles()
        self._tool_profile_list = controller.GetToolProfiles()
        self._all_joints_list = controller.GetConnectedJoints()

        #Get downloader flags from controller attributes
        try:
            # Get ArcTech version numbers from controller attributes if available
            self.clamp_base_name = controller.GetString('ClampsBaseName', False)
        except:
            logger.LogInfo("Uploader Info: Can't access controller attribute: 'ClampsBaseName'")
            logger.LogInfo("Uploader Info: Will use default clamp base name 'CLAMP_'")
        if self.clamp_base_name != '':
            logger.LogInfo("Uploader Info: Found controller attribute: 'ClampsBaseName=" + self.clamp_base_name + "'")
            logger.LogInfo("Uploader Info: Will use default clamp base name 'CLAMP_'")

        # Log available base profiles
        logger.LogInfo("Available Base Profiles:")
        for profile in self._base_profile_list:
            logger.LogInfo(f"- {profile.GetName()}")

        # Select base frame
        try:
            self.uploadRefBaseFrame = controller.GetString('UploadRefBaseFrame', False)
        except:
            logger.LogInfo("Controller attribute 'UploadRefBaseFrame' not defined.")
            logger.LogInfo("Uploader will use 1st available base frame of machine/robot.")
            self.uploadRefBaseFrame = None

        for base_frame in self._base_profile_list:
            if base_frame.GetName() == 'World':
                # 'World' frame is not allowed as reference frame in OLP
                continue
            elif base_frame.GetName() == '':
                # Unnamed frames are most likely OLP frames and are not allowed as reference frames in OLP
                continue
            elif base_frame.GetName() == self.uploadRefBaseFrame:
                self.base_profile_default = base_frame
                logger.LogInfo("Reference Base frame named '" + self.uploadRefBaseFrame + "' found.")
                break
        else:
            # Fallback to the first available base profile if no match was found
            if self._base_profile_list:
                self.base_profile_default = self._base_profile_list[self.base_profile_default_index]
                logger.LogInfo("Reference Base frame not found. Using first available base frame.")
            else:
                logger.LogError("No valid base profile found in the controller.")

        # Select tool frame
        try:
            upload_reference_tool_frame_name = controller.GetString('UploadRefToolFrame', False)
        except:
            logger.LogInfo("Controller attribute 'UploadRefToolFrame' not defined.")
            logger.LogInfo("Uploader will use 1st available tool frame of machine/robot.")
            upload_reference_tool_frame_name = None

        for tool_frame in self._tool_profile_list:
            if tool_frame.GetName() == upload_reference_tool_frame_name:
                self.tool_profile_default = tool_frame
                logger.LogInfo("Reference Tool frame named '" + upload_reference_tool_frame_name + "' found.")
                break
        else:
            # Fallback to the first available tool profile if no match was found
            if self._tool_profile_list:
                self.tool_profile_default = self._tool_profile_list[self.tool_profile_default_index]
                logger.LogInfo("Reference Tool frame not found. Using first available tool frame.")
            else:
                logger.LogError("No valid tool profile found in the controller.")


        self.current_Orientation = [0, 0, 0] 
        # Initialize parsers with operator
        self.shape_parser = ShapeParser(operator, self, self.regshape_patterns, self.shapes)

    def EventsLogging(self, eventList, decription):
      TestList = []
      for evt in eventList:
            aaa =  str(evt.GetName())
            TestList.append(decription + "EVENT: " + aaa)
            for att in evt.GetAttributes():
               bbb = "    " + decription + aaa + " -Attr:" + str(att.GetName()) + "=" + str(att.GetValue())
               TestList.append(bbb)
      return TestList

    # Call Mandatory Uploader Method
    def ParseFile(self, operator: ULPythonUploadOperator, file_object: TextIOWrapper):
        logger = operator.GetLogOperator()
        logger.LogDebug("PrimaXml ParseFile called")
        try:
            self._program_name = os.path.splitext(os.path.basename(file_object.name))[0]
            lines = file_object.readlines()
            xml_data = "".join(line.strip() for line in lines)

            # Comments are ignored when parsing an XML tree
            # but we need the comments for keywords like OperationGroup, etc
            class _CommentedTreeBuilder(ET.TreeBuilder):
                def comment(self, data):
                    self.start("_comment", {})
                    self.data(str.strip(data))
                    self.end("_comment")

            ctb = _CommentedTreeBuilder()
            xp = ET.XMLParser(target=ctb)
            tree = ET.parse(file_object.name, parser=xp)
            root = tree.getroot()
            self.parse_xml_tree(operator, root)
        except ET.ParseError as e:
            logger.LogError(f"XML parsing error: {e}")

    # Call Mandatory Uploader Method
    def Finalize(self, operator: ULPythonUploadOperator):
        logger = operator.GetLogOperator()
        logger.LogDebug("PrimaXml Finalize called")

    def parse_xml_tree(self, operator: ULPythonUploadOperator, root):
        # Program structure items
        program: ULPythonProgram = None
        operation_group: ULPythonOperationGroup = None
        operation: ULPythonOperation = None
        # Motions
        motion_linear: ULPythonMotion = None
        motion_via: ULPythonMotion = None
        motion_circular: ULPythonMotion = None
        motion_regshape: ULPythonMotion = None
        # Events
        events_before: list[ULPythonEvent] = []
        events_after: list[ULPythonEvent] = []
        events_before_regshape: list[ULPythonEvent] = []
        events_after_regshape: list[ULPythonEvent] = []
        current_program: ULPythonProgram = None
        current_operation_group: ULPythonOperationGroup = None
        current_operation: ULPythonOperation = None
        current_motion: ULPythonMotion = None
        current_event: ULPythonEvent = None
        # Attributes
        program_attrib:OlpCorePythonAttribute = None 
        operation_group_attrib:OlpCorePythonAttribute = None
        operation_attrib:OlpCorePythonAttribute = None
        event_attrib:OlpCorePythonAttribute = None
        attribute:OlpCorePythonAttribute = None
        attribute_level = None
        # Get the list of elements
        elements = list(root)
        processed_indices = set()

        i = 0
        while i < len(elements):
            prev_i = i
            
            # Check for regshape patterns
            if i == prev_i:
                i, motion_regshape, events_before_regshape, events_after_regshape = self.shape_parser.parse_regshape(operator, i, elements)
            
            # If no patterns matched, process the element individually
            if i == prev_i:
                self.check_for_slot(operator, i, elements)
                i, program, operation_group, operation, motion_linear, motion_circular = self.process_element(i, operator, elements[i])
                self.ABZeroDeviation = 0.03  # reset to original Value

            if i == prev_i:
                continue  # Line not matched before therefore continue with next line

            # Create E2 items
            if program:
                current_program = program
                program = None
                continue
            
            # if OpGroup AND Op Comment were removed (manual edit by User) we need to activate OpGroup & Op
            setOpGroupAndOperation = False
            if operation_group != None and operation != None:
                setOpGroupAndOperation = True
            
            if operation_group:
                # output collected header lines before the operation group and write into program attributes
                if current_operation_group == None:
                    # getting all Header-Lines (! maybe more than 1024 chars)
                    returnList = self.split_text_line (self._text_event_list)
                    header = "|".join(returnList[0])
                    # Program attributes are not working ==> upload event as a workaround
                    # attribute = self.create_attribute(operator, "UploadHeader", {"Value": header, "Type": str})
                    # attribute_level = AttributeLevel.Program
                    uploadHeader = self.create_event_with_attributes(
                        operator,
                        "UploadFlags",
                        TPINSERTPOS_INSERTBEFORE,
                        {
                            "UploadFlag": {"Value": 'HEADER', "Type": str},
                            "Text": {"Value": header, "Type": str},
                            "MultiLineSeparator": {"Value": "|", "Type": str},
                        }
                    )
                    self.events_before.append(uploadHeader)
                    # -----------------------------------------------------------------
                    # if all collected HeaderLines > 1024 chars (Apt Limitation!)
                    if len(returnList) > 1:
                        for itemList in returnList[1:]:
                           # create further TextEvents if all collected HeaderLines > 1024 (Apt Limitation!)
                           # first is already output with UploadFlags
                           self._text_event_list = itemList
                           self.add_text_event(operator, self.events_before)
                    # -----------------------------------------------------------------
                    # Clearing list
                    self._text_event_list.clear()
                current_operation_group = operation_group
                if current_program:
                    current_program.AddOperationGroup(operation_group)
                    operation_group = None
                if setOpGroupAndOperation == False:
                   continue  # if only OpGroup set, continue. Else, set Operation as well (manually scrapped by User)

            if operation:
                current_operation = operation
                if current_operation_group:
                    current_operation_group.AddOperation(operation)
                    operation = None
                continue

            if motion_linear:
                current_motion = motion_linear
                if current_operation:
                    self.add_text_event(operator, self.events_before)
                    motion_linear.SetEventsBefore(self.events_before)
                    self.events_before.clear()
                    self.events_after.clear()
                    current_operation.AddMotion(motion_linear)
                    self.lastMotionLinear = motion_linear
                    motion_linear = None
                continue

            if motion_circular:
                current_motion = motion_circular
                if current_operation:
                    self.add_text_event(operator, self.events_before)
                    motion_circular.SetEventsBefore(self.events_before)
                    self.events_before.clear()
                    self.events_after.clear()
                    current_operation.AddMotion(motion_circular)
                    motion_circular = None
                continue
            
            if motion_regshape:
                current_motion = motion_regshape
                if current_operation:
                    self.add_text_event(operator, self.events_before)
                    current_operation.AddMotion(motion_regshape)
                    current_motion.SetEventsBefore(self.events_before + events_before_regshape)
                    current_motion.SetEventsAfter(events_after_regshape)
                self.events_before.clear()
                events_before_regshape.clear()
                events_after_regshape.clear()
                motion_regshape = None
                continue

            if attribute:
                if attribute_level is AttributeLevel.Program and current_program:
                    current_program.AddAttribute(attribute)
                if attribute_level is AttributeLevel.Group and current_operation_group:
                    current_operation_group.AddAttribute(attribute)
                if attribute_level is AttributeLevel.Operation and current_operation:
                    current_operation.AddAttribute(attribute)
                attribute = None
                attribute_level = None
                continue
    
    def check_for_slot(self, operator: ULPythonUploadOperator, start_index: int, elements):
        '''check from G01/APPROACH if following is a SLOT and A&B Angles are Zero : don't use "B0.03".'''
        for r in range(start_index + 1, start_index + 4):
            mes = " r=" + str(r) + "(" + str(len(elements)) + ")"
            if r >= len(elements):
                break # we come to the File-End
            if elements[r].tag in ["G01", "APPROACH"]:
                break
            elif elements[r].tag in ["SLOT"]:
                c = float(elements[start_index].get("A", self.lastCoordC))
                a = float(elements[start_index].get("B", self.lastCoordA))
                if abs(a) < 0.001 and abs(c) < 0.001:
                   self.ABZeroDeviation = 0.0
                break

    def split_text_line (self, textList):
        """
        Collected Elements may longer than 1024 Chars (Apt couldn't read more)
        Cut them into handable Lists
        """
        returnList = []
        tempList = []
        iStrLen = 0
        if len(textList):
            for item in textList:
                iStrLen += len(item)
                if iStrLen > 900:
                    returnList.append(tempList)
                    tempList = []
                    iStrLen = 0
                tempList.append(item)
            returnList.append(tempList)
        return returnList
        
    def process_element(self, start_index, operator: ULPythonUploadOperator, element):
        """
        Process individual XML elements that do not fit into patterns.
        """
        program = None
        operation_group = None
        operation = None
        motion_linear = None
        motion_circular = None
        speed = 0
        localFeedFlag = False
        i = start_index
        if 'LocalFeed' in element.attrib:
            local_feed = element.get("LocalFeed", "0")
            speed = int(local_feed) if self.is_numerical(local_feed) else 10000
            # Set a Text-Event "LOCALFEEDFLAG" before the FEED-Event to control the ...B="-15.0" LocalFeed="11000"/>
            if self.is_numerical(local_feed):
               # ... but only numerical Values, not LocalFeed="R4"
               self._text_event_list.append("LOCALFEEDFLAG")
            else:
               localFeedFlag = True
        elif element.tag == 'FEED' and 'Value' in element.attrib:
            feed = element.get("Value", "0")
            speed = int(feed) if self.is_numerical(feed) else 10000
        
        if speed > 0 and localFeedFlag != True:
            speed_event = self.create_event_with_attributes(
                operator,
                "Speed",
                TPINSERTPOS_INSERTBEFORE,
                {
                    "Value": {"Value": speed / 60000, "Type": float},
                    "PathType": {"Value": 'Contour', "Type": str},
                },
            )
            self.add_text_event(operator, self.events_before)
            self.events_before.append(speed_event)
        
        # ======= for Breakpoints =================
        if element.tag == "G01":
            iDummy = start_index
        if i > 23999:
            #aaa = element.tag
            #bbb = self.EventsLogging(self.events_before, "EventsBefore :")
            iDummy = start_index
        # =========================================
        
        # OpGroup and/or Operation Comments might be deleted in manually edited Program
        # Check here to set OpGroup and/or Operation
        if not self._headerCompleted and self._opGroupSet == False:
            operation_group = self.opened_operation_group(operator, element)
            if operation_group != None:
               operation = self.opened_operation(operator, element)
        if self._headerCompleted and self._operationSet == False:
            operation = self.opened_operation(operator, element)
        
        # ============== on we go parsing ============================
        if element.tag == "PROGRAM_BEGIN":
            program = operator.CreateEmptyProgram()
            program.SetName(self._program_name)
            program.SetIsMainProgram(True)
        elif element.tag == "_comment":
            # Parse operation group and operation names
            if operation_group == None:
               operation_group = self.parse_operation_group(operator, element.text)
            operation = self.parse_operation(operator, element.text)
            # Convert to XML comment
            commentString = ET.tostring(element, encoding='unicode').strip()
            commentString = commentString.replace('<_comment>', '<!-- ').replace('</_comment>', ' -->').replace('<', '<').replace('>', '>')
            commentString = commentString.replace('&lt;', '<').replace('&gt;', '>')
            if 'Start of OperationGroup' in commentString and not self._headerCompleted:
                self._headerCompleted = True
            self._text_event_list.append(commentString)
        elif element.tag == "G113":
            self.process_g113_g114_base_frame(operator, element)
            self.add_element_to_text_event_list(element)
        elif element.tag == "G114":
            self.process_g113_g114_base_frame(operator, element)
            self.add_element_to_text_event_list(element)
        elif element.tag == "G93":
            self.add_element_to_text_event_list(element)
        elif self._headerCompleted:
            # Handle various tags after header completion
            if element.tag == "FEED":
                pass
            elif element.tag in ["FLY_ON", "FLY_OFF"]:
                # Parse flyby event
                flyby_event = self.handle_flyby_event(operator, element)
                flyby_event_for_last = self.handle_flyby_event(operator, element, TPINSERTPOS_INSERTAFTER) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(flyby_event)
                self.events_after.append(flyby_event_for_last)
            elif element.tag == "ACCURACY":
                cutting_accuracy_event = self.handle_cutting_accuracy_event(operator, element)
                cutting_accuracy_event_for_last = self.handle_cutting_accuracy_event(operator, element, TPINSERTPOS_INSERTAFTER) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(cutting_accuracy_event)
                self.events_after.append(cutting_accuracy_event_for_last)
            elif element.tag == "SENSOR_ON":
                sensor_on_event = self.handle_sensor_on_event(operator, element) # store for Footer Section
                sensor_on_event_for_last = self.handle_sensor_on_event(operator, element, TPINSERTPOS_INSERTAFTER)
                self.add_text_event(operator, self.events_before)
                self.events_before.append(sensor_on_event)
                self.events_after.append(sensor_on_event_for_last)
            elif element.tag == "SENSOR_OFF":
                sensor_off_event = self.create_event_with_attributes(operator, "SensorOff", TPINSERTPOS_INSERTBEFORE, {})
                sensor_off_event_for_last = self.create_event_with_attributes(operator, "SensorOff", TPINSERTPOS_INSERTAFTER, {}) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(sensor_off_event)
                self.events_after.append(sensor_off_event_for_last)
            elif element.tag == "SET_SENSOR_GAP":
                lh_on_value = float(element.get("Gap", "0"))
                lh_on_event = self.create_event_with_attributes(operator, "SensorGap", TPINSERTPOS_INSERTBEFORE, {
                    "SensorGapValue": {"Value": lh_on_value/1000, "Type": float},
                })
                lh_on_event_for_last = self.create_event_with_attributes(operator, "SensorGap", TPINSERTPOS_INSERTAFTER, {
                    "SensorGapValue": {"Value": lh_on_value/1000, "Type": float},
                }) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(lh_on_event)
                self.events_after.append(lh_on_event_for_last)
            elif element.tag == "LH_ON":
                lh_on_value = float(element.get("ChordalError", "0"))
                lh_on_event = self.create_event_with_attributes(operator, "LookAheadOn", TPINSERTPOS_INSERTBEFORE, {
                    "LookAheadDistance": {"Value": lh_on_value/1000, "Type": float},
                })
                lh_on_event_for_last = self.create_event_with_attributes(operator, "LookAheadOn", TPINSERTPOS_INSERTAFTER, {
                    "LookAheadDistance": {"Value": lh_on_value/1000, "Type": float},
                }) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(lh_on_event)
                self.events_after.append(lh_on_event_for_last)
            elif element.tag == "LH_OFF":
                lh_off_event = self.create_event_with_attributes(operator, "LookAheadOff", TPINSERTPOS_INSERTBEFORE, {})
                lh_off_event_for_last = self.create_event_with_attributes(operator, "LookAheadOff", TPINSERTPOS_INSERTAFTER, {}) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(lh_off_event)
                self.events_after.append(lh_off_event_for_last)
            elif element.tag in ['WORK_ON', 'MARKING_ON', 'WELD_ON']:
                # Parse laser on event
                laser_on_type = element.tag
                laser_line_value = int(element.get("LaserLine", "1"))
                piercing_type_value = int(element.get("PiercingType", "1"))
                try:
                    laser_on_technical_param_type = int(laser_line_value)
                except ValueError:
                    laser_on_technical_param_type = 1
                try:
                    laser_on_piercing_type = int(piercing_type_value)
                except ValueError:
                    laser_on_piercing_type = 1
                laser_on_event = self.handle_laser_on_event(
                    operator, laser_on_type, laser_on_technical_param_type, laser_on_piercing_type)
                laser_on_event_for_last = self.handle_laser_on_event(
                    operator, laser_on_type, laser_on_technical_param_type, laser_on_piercing_type, TPINSERTPOS_INSERTAFTER) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(laser_on_event)
                self.events_after.append(laser_on_event_for_last)
            elif element.tag in ['WORK_OFF', 'MARKING_OFF', 'WELD_FF']:
                # Parse laser off event
                laser_off_event = self.create_event_with_attributes(operator, "LaserOff", TPINSERTPOS_INSERTBEFORE, {})
                laser_off_event_for_last = self.create_event_with_attributes(operator, "LaserOff", TPINSERTPOS_INSERTAFTER, {}) # store for Footer Section
                self.add_text_event(operator, self.events_before)
                self.events_before.append(laser_off_event)
                self.events_after.append(laser_off_event_for_last)
            elif element.tag in ["G01", "APPROACH", "RETRACT"]:
                # Parse linear motion
                if element.tag == 'RETRACT':
                    # empty List on Retract to have only Items that are appearing from now on
                    self.events_after.clear()
                if element.tag in ["APPROACH", "RETRACT"]:
                    upload_flag_event = self.create_event_with_attributes(
                        operator,
                        "UploadFlags",
                        TPINSERTPOS_INSERTBEFORE,
                        {
                            "UploadFlag": {"Value": element.tag, "Type": str},
                        },
                    )
                    self.add_text_event(operator, self.events_before)
                    self.events_before.append(upload_flag_event)
                motion_linear = self.parse_linear_motion(operator, element)
            elif element.tag == "G104":
                # Parse circular motion
                motion_circular = self.parse_circular_motion(operator, element)
            elif element.tag == 'PROGRAM_END':
                # at Program End, output all stored Stuff from last Move to ProgramEnd (TextEvent after lastMotionLinear)
                self.add_text_event(operator, self.events_after, TPINSERTPOS_INSERTAFTER)
                newBeforeEvents = self.reorderBeforeEventsForEnd(self.events_before)
                self.lastMotionLinear.SetEventsAfter(newBeforeEvents + self.events_after)
            else:
                # Everything unknown gets collected in a list to be stored in a multi-line TextEvent attached to the next motion
                self.add_element_to_text_event_list(element)
        else:
            # Everything unknown gets collected in a list to be stored in a multi-line TextEvent attached to the next motion
            self.add_element_to_text_event_list(element)
        i += 1
        return i, program, operation_group, operation, motion_linear, motion_circular
    
    def reorderBeforeEventsForEnd(self, eventList):
      '''Filter out the Events from self.events_before for ProgramEnd, bec. they were already set in xxxxx_for_last as events_after'''
      newEvtList = []
      if eventList == []:
          return newEvtList
      chkEvtList = ["LaserOn","LaserOff","LookAheadOn","LookAheadOff","SensorOff","SensorOn","SensorGap","Accuracy","CuttingAccuracy"]
      for evt in eventList:
         if not evt.GetName() in chkEvtList:
            evt.SetInsertPosition(TPINSERTPOS_INSERTAFTER)
            newEvtList.append(evt)
      return newEvtList

    def add_element_to_text_event_list(self, element):
        textString = ET.tostring(element, encoding='unicode').strip()
        textString = textString.replace('&lt;', '<').replace('&gt;', '>').replace(' />', '/>')
        self._text_event_list.append(textString)

    def add_text_event(self, operator: ULPythonUploadOperator, events: list [ULPythonEvent], evtPosition:int = TPINSERTPOS_INSERTBEFORE):
        # output collected unparsed lines before the operation group and write into program attributes
        if not self._text_event_list == []:
            text = "|".join(self._text_event_list[:])
            if "|" in text:
                isMultiLine = True
            else:
                isMultiLine = False
            textEvent = self.create_event_with_attributes(
                operator,
                "TextEvent",
                evtPosition,
                {
                    "Text": {"Value": text, "Type": str},
                    "IsMultiLine": {"Value": isMultiLine, "Type": bool},
                    "MultiLineSeparator": {"Value": "|", "Type": str},
                },
            )

           # Clearing list
            self._text_event_list.clear()
            events.append(textEvent)

    def opened_operation_group(self, operator: ULPythonUploadOperator, element):
        foundOpStart = False
        if element.text != None:
            if "Start of Operation:" in element.text:
                foundOpStart = True
        if element.tag in ["HOLE_ACCURACY", "G01", "G104"] or foundOpStart:
            group_name = "DefaultOperationGroup001"
            ul_operation_group = operator.CreateEmptyOperationGroup()
            ul_operation_group.SetName(group_name)
            self._headerCompleted = True
            self._opGroupSet = True
            return ul_operation_group
        return None
    
    def opened_operation(self, operator: ULPythonUploadOperator,element):
        if element.tag in ["HOLE_ACCURACY", "G01", "G104"]:
            operation_name = "DefaultOperation001"
            ul_operation = operator.CreateEmptyOperation()
            ul_operation.SetName(operation_name)
            ul_operation.SetUsedBaseProfile(self.base_profile_default)
            ul_operation.SetUsedToolProfile(self.tool_profile_default)
            self._operationSet = True
            return ul_operation
        return None
        
    def parse_program(self, operator: ULPythonUploadOperator, text: str):
        program_pattern = re.compile(r"^PROGRAM NAME\s+:\s+(\w+)")
        match = program_pattern.search(text)
        if match:
            program_name = match.group(1)
            new_program = operator.CreateEmptyProgram()
            new_program.SetName(program_name)
            new_program.SetIsMainProgram(True)
            return new_program
        return None

    def parse_operation_group(self, operator: ULPythonUploadOperator, text: str):
        operation_group_pattern = re.compile(r'Start of OperationGroup:\s*"([^"]+)"')
        match = operation_group_pattern.search(text)
        if match:
            group_name = match.group(1)
            ul_operation_group = operator.CreateEmptyOperationGroup()
            ul_operation_group.SetName(group_name)
            self._opGroupSet = True
            return ul_operation_group
        return None

    def parse_operation(self, operator: ULPythonUploadOperator, text: str):
        operation_pattern = re.compile(r'Start of Operation:\s*"([^"]+)"')
        match = operation_pattern.search(text)
        if match:
            operation_name = match.group(1)
            ul_operation = operator.CreateEmptyOperation()
            ul_operation.SetName(operation_name)
            ul_operation.SetUsedBaseProfile(self.base_profile_default)
            ul_operation.SetUsedToolProfile(self.tool_profile_default)
            self._operationSet = True
            return ul_operation
        return None

    def parse_linear_motion(self, operator: ULPythonUploadOperator, element):
        ul_motion = operator.CreateEmptyMotion()
        ul_motion.SetMotionType(MotionType.Linear)
        ul_position = operator.CreateEmptyPosition()
        ul_position.SetProcessType(ProcessType.ProcessCurve)
        ul_position.SetTargetType(TargetType.Cartesian)
        if ul_position:
            ul_motion.SetPosition(ul_position)
            self.parse_linear_target(operator, ul_position, element)
            return ul_motion
        return None

    def parse_linear_target(self, operator: ULPythonUploadOperator, ul_position: ULPythonPosition, element):
        x = float(element.get("X", self.lastCoordX)) / 1000
        y = float(element.get("Y", self.lastCoordY)) / 1000
        z = float(element.get("Z", self.lastCoordZ)) / 1000
        c = float(element.get("A", self.lastCoordC))
        a = float(element.get("B", self.lastCoordA))
        # store Values for modality
        self.lastCoordX = x * 1000
        self.lastCoordY = y * 1000
        self.lastCoordZ = z * 1000
        self.lastCoordC = c
        self.lastCoordA = a
        # set Values
        if abs(a) < 0.001:  # if a  0:
            a = self.ABZeroDeviation # 0.03
        ul_position.SetXYZ((x, y, z))
        rotation_matrix = self.compute_rotation_matrix_ca(np.radians(c), np.radians(a))
        config = 'Posture_1' if a >= 0 else 'Posture_2'
        turn_c = int(c // 360)
        turn_a = 0 if a >= 0 else -1
        turn = f"{turn_c},{turn_a}"
        rx, ry, rz = BaseParser.extract_euler_angles(rotation_matrix)
        self.current_Orientation = [rz, ry,rx]
        ul_position.SetOrientation(tuple(self.current_Orientation))
        ul_position.SetConfig(config)
        ul_position.SetTurn(turn)

    def parse_circular_motion(self, operator: ULPythonUploadOperator, element):
        ul_motion_cir = operator.CreateEmptyMotion()
        ul_motion_cir.SetMotionType(MotionType.Circular)
        ul_position_via = operator.CreateEmptyPosition()
        ul_position_cir = operator.CreateEmptyPosition()
        if not ul_position_via or not ul_position_cir:
            return None
        ul_position_via.SetProcessType(ProcessType.ViaPoint)
        ul_position_via.SetTargetType(TargetType.Cartesian)
        ul_position_cir.SetProcessType(ProcessType.ProcessCurve)
        ul_position_cir.SetTargetType(TargetType.Cartesian)
        ul_motion_cir.SetViaPosition(ul_position_via)
        ul_motion_cir.SetPosition(ul_position_cir)
        self.parse_circular_target(operator, ul_position_via, ul_position_cir, element)
        return ul_motion_cir

    def parse_circular_target(self, operator: ULPythonUploadOperator, ul_position_via: ULPythonPosition, ul_position_cir: ULPythonPosition, element):
        x = float(element.get("X", self.lastCoordX)) / 1000
        y = float(element.get("Y", self.lastCoordY)) / 1000
        z = float(element.get("Z", self.lastCoordZ)) / 1000
        c = float(element.get("A", self.lastCoordC))
        a = float(element.get("B", self.lastCoordA))
        x_via = float(element.get("I", self.lastCoordI)) / 1000
        y_via = float(element.get("J", self.lastCoordJ)) / 1000
        z_via = float(element.get("K", self.lastCoordK)) / 1000
        # store Values for modality
        self.lastCoordX = x * 1000
        self.lastCoordY = y * 1000
        self.lastCoordZ = z * 1000
        self.lastCoordC = c
        self.lastCoordA = a
        self.lastCoordI = x_via * 1000
        self.lastCoordJ = y_via * 1000
        self.lastCoordK = z_via * 1000
        # set Values
        if abs(a) < 0.001:  # if a  0:
            a = self.ABZeroDeviation # 0.03
        ul_position_cir.SetXYZ((x, y, z))
        ul_position_via.SetXYZ((x_via, y_via, z_via))
        rotation_matrix = self.compute_rotation_matrix_ca(np.radians(c), np.radians(a))
        config = 'Posture_1' if a >= 0 else 'Posture_2'
        turn_c = int(c // 360)
        turn_a = 0 if a >= 0 else -1
        turn = f"{turn_c},{turn_a}"
        rx, ry, rz = self.extract_euler_angles(rotation_matrix)
        self.current_Orientation = [rz, ry,rx]
        ul_position_cir.SetOrientation(tuple(self.current_Orientation))
        ul_position_cir.SetConfig(config)
        ul_position_cir.SetTurn(turn)

    @classmethod
    def create_event_with_attributes(cls, operator: ULPythonUploadOperator, event_name, insert_pos, attributes: dict):
        event: ULPythonEvent = operator.CreateEmptyEvent()
        event.SetName(event_name)
        event.SetInsertPosition(insert_pos)
        if attributes is None:
            attributes = {}
        for name, attribute_data in attributes.items():
            attribute = cls.create_attribute(operator, name, attribute_data)
            event.AddAttribute(attribute)
        return event

    @classmethod
    def create_attribute(cls, operator: ULPythonUploadOperator, name: str, attribute_data: dict = None):
        if attribute_data is None:
            attribute_data = {"Value": None, "Type": str}
        value = attribute_data["Value"]
        attribute_type = attribute_data["Type"]
        attribute_creator: OlpCorePythonAttributeSetterOperator = operator.GetAttributeSetterOperator()
        attribute_creator_map = {
            float: attribute_creator.CreateWritingDoubleAttributesObject,
            int: attribute_creator.CreateWritingIntAttributesObject,
            str: attribute_creator.CreateWritingStringAttributesObject,
            bool: attribute_creator.CreateWritingBoolAttributesObject,
            enumerate: attribute_creator.CreateWritingLiteralAttributesObject,
        }
        if attribute_type not in attribute_creator_map:
            raise TypeError(f"Unsupported attribute type: {attribute_type}")
        attribute = attribute_creator_map[attribute_type]()
        if attribute_type == enumerate and "Values" in attribute_data:
            values = attribute_data["Values"]
            attribute.SetValues(values)
        attribute.SetName(name)
        attribute.SetValue(value)
        return attribute

    def process_g113_g114_base_frame(self, operator: ULPythonUploadOperator, element):
        """
        Process a single XML element which could be G113 or G114. 
        If G113, store its attributes. If G114 and a stored G113 exists, compute offsets.
        """
        tag = element.tag
        attrs = element.attrib

        if tag == "G113":
            # Store G113 attributes for later use
            self.last_g113_attrs = attrs

        elif tag == "G114":
            # If we have a stored G113, we can compute the offset
            if self.last_g113_attrs is not None:
                # Extract G113 attributes
                G113_x = float(self.last_g113_attrs.get("Xp1", "0")) / 1000.0
                G113_y = float(self.last_g113_attrs.get("Yp1", "0")) / 1000.0
                G113_z = float(self.last_g113_attrs.get("Zp1", "0")) / 1000.0

                # Extract G114 attributes
                G114_x = float(attrs.get("Xp1", "0")) / 1000.0
                G114_y = float(attrs.get("Yp1", "0")) / 1000.0
                G114_z = float(attrs.get("Zp1", "0")) / 1000.0

                x_offset = G114_x - G113_x
                y_offset = G114_y - G113_y
                z_offset = G114_z - G113_z

                baseName = str(self.base_profile_default.GetName())
                if self.base_profile_default.GetName() == "":
                    baseName = self.uploadRefBaseFrame
                self.base_profile_default = operator.CreateOlpBaseFrameProfileFromPositionRotation(
                    baseName,
                    x_offset, y_offset, z_offset, 0.0, 0.0, 0.0
                )

                # Reset after processing
                self.last_g113_attrs = None
            else:
                # If no G113 is stored, you might just skip or store G114 info
                # until a G113 appears. For now, do nothing or log a warning.
                pass

    @classmethod
    def handle_flyby_event(cls, operator: ULPythonUploadOperator, element, evtPosition:int = TPINSERTPOS_INSERTBEFORE):
        if element.tag in ["FLY_ON", "FLY_OFF"]:
            state = "Distance" if element.tag == "FLY_ON" else "Velocity"
            value = 0.001234 if element.tag == "FLY_ON" else 0.0
            flyby_event = cls.create_event_with_attributes(
                operator,
                "Accuracy",
                evtPosition,
                {
                    "Value": {"Value": value, "Type": float},
                    "Criteria": {"Value": state, "Type": str},
                    "PathType": {"Value": "Contour", "Type": str},
                },
            )
            return flyby_event
        else:
            return None

    @classmethod
    def handle_cutting_accuracy_event(cls, operator: ULPythonUploadOperator, element, evtPosition:int = TPINSERTPOS_INSERTBEFORE):
        if element.tag == "ACCURACY":
            cutting_accuracy_type_value = element.get("Level", "99")
            cutting_accuracy_types = ["99:Shorter", "96:Longer", "0:Deactivated"]
            # Create a dictionary to map values to the full strings
            cutting_accuracy_map = {item.split(":")[0]: item for item in cutting_accuracy_types}
            # Use the dictionary to get the full string
            cutting_accuracy_type = cutting_accuracy_map.get(cutting_accuracy_type_value, "Unknown")
            cutting_accuracy_event = cls.create_event_with_attributes(
                operator,
                "CuttingAccuracy",
                evtPosition,
                {
                    "CuttingAccuracyType": {"Value": cutting_accuracy_type, "Type": enumerate, "Values": cutting_accuracy_types},
                    "CuttingAccuracyTypeVal": {"Value": int(cutting_accuracy_type_value), "Type": int},
                },
            )
            return cutting_accuracy_event
        else:
            return None

    @classmethod
    def handle_clamps_event(cls, operator: ULPythonUploadOperator, element, clamp_base_name):
        logger = operator.GetLogOperator()
        clamp_name = clamp_base_name + '5'
        resource: OlpCorePythonResource = None
        resources: list[OlpCorePythonResource] = operator.GetController().GetResources()
        for r in range(0, len(resources)):
            if resources[r].GetItemType().value == FSITEMTYPE_PERIPHERAL:
                resource = resources[r]
                # if resource.GetName() == clamp_name:
                #     clamp_resource = resource.GetAttributes()
                #     clamp_attributes = clamp_resource.GetAttributes()
                #     attribute: OlpCorePythonAttribute
                #     for attribute in range(0, len(clamp_attributes)):
                #         attribute_name = attribute.GetName()
        
        # if element.tag == "SENSOR_ON":
        #     sensor_on_type_value = element.get("LaserLine", "1")
        #     sensor_on_types = ["1:Easy", "2:Medium", "3:Hard", "4:Special", "5:Fast"]
        #     # Create a dictionary to map values to the full strings
        #     sensor_on_map = {item.split(":")[0]: item for item in sensor_on_types}
        #     # Use the dictionary to get the full string
        #     sensor_on_type = sensor_on_map.get(sensor_on_type_value, "Unknown")
        #     sensor_on_event = cls.create_event_with_attributes(
        #         operator,
        #         "SensorOn",
        #         TPINSERTPOS_INSERTBEFORE,
        #         {
        #             "SensorOnType": {"Value": sensor_on_type, "Type": enumerate, "Values": sensor_on_types},
        #         },
        #     )
        #     return sensor_on_event
        # else:
        #     return None

    @classmethod
    def handle_sensor_on_event(cls, operator: ULPythonUploadOperator, element, evtPosition:int = TPINSERTPOS_INSERTBEFORE):
        if element.tag == "SENSOR_ON":
            sensor_on_type_value = element.get("LaserLine", "1")
            sensor_on_types = ["1:Easy", "2:Medium", "3:Hard", "4:Special", "5:Fast"]
            # Create a dictionary to map values to the full strings
            sensor_on_map = {item.split(":")[0]: item for item in sensor_on_types}
            # Use the dictionary to get the full string
            sensor_on_type = sensor_on_map.get(sensor_on_type_value, "Unknown")
            sensor_on_event = cls.create_event_with_attributes(
                operator,
                "SensorOn",
                evtPosition,
                {
                    "SensorOnType": {"Value": sensor_on_type, "Type": enumerate, "Values": sensor_on_types},
                },
            )
            return sensor_on_event
        else:
            return None

    @classmethod
    def handle_laser_on_event(cls, operator: ULPythonUploadOperator, laser_on_type: str, technical_parameter_index: int, piercing_type_index: int, evtPosition:int = TPINSERTPOS_INSERTBEFORE):
        """Creates a LaserOn event based on the provided parameters.

        Args:
            operator: The operator instance to be used for creating events.
            laser_on_type: The type of laser on event ("WORK_ON", "MARKING_ON", "WELD_ON").
            technical_parameter_index: The index of the technical parameter to be used for the event.
            piercing_type_index: The index of the piercing type to be used for the event.

        Returns:
            Event: The created LaserOn event.
        """
        cutting_type = {
            "WORK_ON": "CUTTING",
            "MARKING_ON": "MARKING",
            "WELD_ON": "WELDING"
        }.get(laser_on_type, "CUTTING")

        try:
            technical_parameter = LCP_TECHNICAL_PARAM_TYPE_LITERALS[technical_parameter_index - 1]
        except IndexError:
            technical_parameter = LCP_TECHNICAL_PARAM_TYPE_LITERALS[0]

        try:
            piercing_type = LCP_PIERCING_TYPE_LITERALS[piercing_type_index - 1]
        except IndexError:
            piercing_type = LCP_PIERCING_TYPE_LITERALS[0]

        return cls.create_event_with_attributes(
            operator,
            "LaserOn",
            evtPosition,
            {
                "LaserOnCuttingType": {"Value": cutting_type, "Type": enumerate, "Values": LCP_CUTTING_TYPE_LITERALS},
                "LaserOnTechnicalParamType": {"Value": technical_parameter, "Type": enumerate, "Values": LCP_TECHNICAL_PARAM_TYPE_LITERALS},
                "LaserOnPiercingType": {"Value": piercing_type, "Type": enumerate, "Values": LCP_PIERCING_TYPE_LITERALS},
            },
        )

