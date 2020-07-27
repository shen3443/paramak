
import math
from collections import Iterable

import cadquery as cq 

from paramak import Shape

from hashlib import blake2b

class SweepMixedShape(Shape):
    """Sweeps a 2D shape created from points connected with straight, spline or circular 
       connections along a defined spline to create a 3D CadQuery solid.
    
       :param points: A list of XY, YZ or XZ coordinates connected by straight, spline or circular
         connections which define the 2D shape to be swept
       :type points: a list of tuples
       :param path_points: A list of XY, YZ or XZ coordinates which define the spline path along
            which the 2D shape is swept
       :type path_points: a list of tuples
       :param workplane: Workplane in which the 2D shape to be swept is defined
       :type workplane: str
       :param path_workplane: Workplane in which the spline path is defined
       :type path_workplane: str
       :param stp_filename: the filename used when saving stp files as part of a reactor
       :type stp_filename: str
       :param color: the color to use when exporting the shape in html graphs or png images
       :type color: Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences of,
           3 or 4 floats respectively each in the range 0-1
       :param azimuth_placement_angle: the angle or angles to use when rotating the 
           shape on the azimuthal axis
       :type azimuth_placement_angle: float or iterable of floats
       :param cut: An optional cadquery object to perform a boolean cut with this object
       :type cut: cadquery object
       :param material_tag: The material name to use when exporting the neutronics description
       :type material_tag: str
       :param name: The legend name used when exporting a html graph of the shape
       :type name: str
    """

    def __init__(
        self,
        points,
        path_points,
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

        self.path_points = path_points
        self.path_workplane = path_workplane
        self.hash_value = hash_value
        self.cut = cut

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
        """Creates a 3d solid by sweeping a 2D shape created from points and straight,
        spline or circle connections along a defined spline

        :return: a 3d solid volume
        :rtype: a CadQuery solid
        """

        # Creates hash value for current solid
        self.hash_value = self.get_hash()

        path = cq.Workplane(self.path_workplane).spline(self.path_points)
        distance = float(self.path_points[-1][1] - self.path_points[0][1])

        # The coordinate system in CQ is right-handed so positive offsets are in the negative direction for some workplanes
        # self.workplane can only take certain values so some tests defined below are not required
        if self.workplane == "XZ" or self.workplane == "YX" or self.workplane == "ZY":
            distance = -distance

        # obtains the first two values of the points list
        XZ_points = [(p[0], p[1]) for p in self.points]

        # obtains the last values of the points list
        connections = [p[2] for p in self.points[:-1]]

        current_linetype = connections[0]
        current_points_list = []
        instructions = []
        # groups together common connection types
        for i, c in enumerate(connections):
            if c == current_linetype:
                current_points_list.append(XZ_points[i])
            else:
                current_points_list.append(XZ_points[i])
                instructions.append({current_linetype: current_points_list})
                current_linetype = c
                current_points_list = [XZ_points[i]]
        instructions.append({current_linetype: current_points_list})

        if list(instructions[-1].values())[0][-1] != XZ_points[0]:
            keyname = list(instructions[-1].keys())[0]
            instructions[-1][keyname].append(XZ_points[0])

        solid = cq.Workplane(self.workplane).workplane(offset=self.path_points[0][1]).moveTo(self.path_points[0][0], 0).workplane()

        for entry in instructions:
            if list(entry.keys())[0] == "spline":
                solid = solid.spline(listOfXYTuple=list(entry.values())[0])
            if list(entry.keys())[0] == "straight":
                solid = solid.polyline(list(entry.values())[0])
            if list(entry.keys())[0] == "circle":
                p0 = list(entry.values())[0][0]
                p1 = list(entry.values())[0][1]
                p2 = list(entry.values())[0][2]
                solid = solid.moveTo(p0[0],p0[1]).threePointArc(p1, p2)

        solid = solid.close().moveTo(-self.path_points[0][0], 0).workplane(offset=distance).moveTo(self.path_points[-1][0], 0).workplane()

        for entry in instructions:
            if list(entry.keys())[0] == "spline":
                solid = solid.spline(listOfXYTuple=list(entry.values())[0])
            if list(entry.keys())[0] == "straight":
                solid = solid.polyline(list(entry.values())[0])
            if list(entry.keys())[0] == "circle":
                p0 = list(entry.values())[0][0]
                p1 = list(entry.values())[0][1]
                p2 = list(entry.values())[0][2]
                solid = solid.moveTo(p0[0],p0[1]).threePointArc(p1, p2)

        solid = solid.close().sweep(path, multisection=True)

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
