
import math
from collections import Iterable 
from hashlib import blake2b 

import cadquery as cq 

from paramak import Shape 
from paramak.utils import cut_solid, intersect_solid, union_solid


class SweepCircleShape(Shape):
    """Sweeps a circle along a defined spline path to create a 3D CadQuery solid.

       Args:
           points (list): unused variable which defaults to None
           radius (float): radius of 2D circle to be swept
           path_points (a list of tuples): a list of XY, YZ or XZ coordinates which define the
               spline path along which the 2D shape is swept
           workplane (str): workplane in which the 2D shape to be swept is defined
           path_workplane (str): workplane in which the spline path is defined
           stp_filename (str): the filename used when saving stp files as part of a reactor
           color (Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences of 3 or 4 floats
               respectively each in the range 0-1): the color to use when exporting the shape in
               html graphs or png images
           azimuth_placement_angle (float or iterable of floats): the angle or angles to use when 
               rotating the shape on the azimuthal axis
           cut (cadquery object): an optional cadquery object to perform a boolean cut with this object
           intersect (cadquery object): an optional cadquery object to perform a boolean intersect with
                this object
           union (cadquery object): an optional cadquery object to perform a boolean union with this object
           material_tag (str): the material name to use when exporting the neutronics description
           name (str): the legend name used when exporting a html graph of the shape
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
        material_tag=None,
        name=None,
        cut=None,
        intersect=None,
        union=None,       
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
        self.intersect = intersect 
        self.union = union

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
    def cut(self, value):
        self._cut = value

    @property
    def intersect(self):
        return self._intersect

    @intersect.setter
    def intersect(self, value):
        self._intersect = value

    @property
    def union(self):
        return self._union

    @union.setter
    def union(self, value):
        self._union = value

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
            solid = cq.Workplane(self.path_workplane)   # rotate in plane of the path
            
            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate((0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)
    
        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            solid = cut_solid(solid, self.cut)

        # If an intersect is provided then perform a boolean intersect
        if self.intersect is not None:
            solid = intersect_solid(solid, self.intersect)

        # If a union is provided then perform a boolean union
        if self.union is not None:
            solid = union_solid(solid, self.union)

        self.solid = solid

        return solid
