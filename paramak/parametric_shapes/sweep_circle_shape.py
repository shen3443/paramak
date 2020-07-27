
import math
from collections import Iterable

import cadquery as cq 

from paramak import Shape

from hashlib import blake2b


class SweepCircleShape(Shape):
    """Sweeps a circle along a defined spline to create a 3D CadQuery solid.
    
       :param points: unused variable which defaults to None.
       :type points: list
       :param radius: radius of 2D circle to be swept
       :type radius: float
       :param path_points: a list of XY, YZ or XZ coordinates which define the spline path along
           which the circle is swept
       :type path_points: a list of tuples
       :param workplane: workplane in which the 2D shape to be swept is defined
       :type workplane: str
       :param path_workplane: workplane in which the spline path is defined
       :type path_workplane: str
       :param stp_filename: the filename used when saving stp files as part of a reactor
       :type stp_filename: str
       :param color: the color to use when exporting the shape in html graphs or png
       :type color: Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences of,
           3 or 4 floats respectively each in the range 0-1
       :param azimuth_placement_angle: the angle or angles to use when rotating the
           shape on the azimuthal axis
       :type azimuth_placement_angle: float or iterable of floats
       :param cut: an optional cadquery object to perform a boolean cut with this object
       :type cut: cadquery object
       :param material_tag: the material name to use when exporting the neutronics description
       :type material_tag: str
       :param name: the legend name used when exporting a html graph of the shape
       :type name: str
    """

    def __init__(
        self,
        radius,
        path_points,
        points=None,
        path_workplane="XZ",
        workplane="XY",
        stp_filename=None,
        solid=None,
        color=None,
        azimuth_placement_angle=0,
        cut=None,
        material_tag=None,
        name=None,
        hash_value=None,
    ):

        super().__init__(
            points,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            workplane,
        )

        self.radius = radius
        self.path_points = path_points
        self.path_workplane = path_workplane
        self.hash_value = hash_value
        self.cut = cut

    # self.points is not used to construct this parametric shape but Shape still requires self.points to have value
    # define a new points getter and setter to ensure self.point=None and raises error if a user tries to modify this
    @property
    def points(self):
        return self._points
    
    @points.setter
    def points(self, values):
        if values != None:
            raise ValueError(
                "points is an unused variable in this parametric shape"
            )
        else:
            self._points = values

    @property
    def cut(self):
        return self._cut

    @cut.setter
    def cut(self, cut):
        self._cut = cut

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, solid):
        self._solid = solid

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def path_points(self):
        return self._path_points

    @path_points.setter
    def path_points(self, value):
        self._path_points = value

    @property
    def path_workplane(self):
        return self._path_workplane

    @path_workplane.setter
    def path_workplane(self, value):
        if value[0] != self.workplane[0]:
            raise ValueError(
                "workplane and path_workplane must start with the same letter"
            )
        elif value == self.workplane:
            raise ValueError(
                "workplane and path_workplane must be different"
            )
        else:
            self._path_workplane = value

    @property
    def hash_value(self):
        return self._hash_value

    @hash_value.setter
    def hash_value(self, value):
        self._hash_value = value

    def get_hash(self):
        hash_object = blake2b()
        hash_object.update(str(self.points).encode('utf-8') +
                           str(self.radius).encode('utf-8') +
                           str(self.path_points).encode('utf-8') +
                           str(self.path_workplane).encode('utf-8') +
                           str(self.workplane).encode('utf-8') +
                           str(self.name).encode('utf-8') +
                           str(self.color).encode('utf-8') +
                           str(self.material_tag).encode('utf-8') +
                           str(self.stp_filename).encode('utf-8') +
                           str(self.azimuth_placement_angle).encode('utf-8') +
                           str(self.cut).encode('utf-8')
        )
        value = hash_object.hexdigest()
        return value

    def create_solid(self):
        """Creates a 3d solid by sweeping a 2D shape created from circular connections
        along a defined spline

        :return: a 3d solid volume
        :rtype: a CadQuery solid
        """

        # Creates hash value for current solid
        self.hash_value = self.get_hash()

        # at the moment, this simply uses the start and end points of the spline to position the faces

        path = cq.Workplane(self.path_workplane).spline(self.path_points)
        distance = float(self.path_points[-1][1] - self.path_points[0][1])

        # The coordinate system in CQ is right-handed so positive offsets are in the negative direction for some workplanes
        # self.workplane can only take certain values so some tests defined below are not required
        if self.workplane == "XZ" or self.workplane == "YX" or self.workplane == "ZY":
            distance = -distance

        solid = (
            cq.Workplane(self.workplane)
            .workplane(offset=self.path_points[0][1])
            .moveTo(self.path_points[0][0], 0)
            .workplane()
            .circle(self.radius)
            .moveTo(-self.path_points[0][0], 0)
            .workplane(offset=distance)
            .moveTo(self.path_points[-1][0], 0)
            .workplane()
            .circle(self.radius)
            .sweep(path, multisection=True)
        )

        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(solid.rotate((0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.path_workplane)   # rotate in plane of the path, NOT the face

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate((0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)

        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            # Allows for multiple cuts to be applied
            if isinstance(self.cut, Iterable):
                for cutting_solid in self.cut:
                    solid = solid.cut(cutting_solid.solid)
            else:
                solid = solid.cut(self.cut.solid)

        self.solid = solid

        return solid
