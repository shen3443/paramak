from collections import Iterable

import cadquery as cq

from paramak import Shape


class ExtrudeSplineShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with spline connections

    Args:
        points (list of tuples each containing X (float), Z (float)): a list of
            XZ coordinates connected by spline connections. For example
            [(2.,1.), (2.,2.), (1.,2.), (1.,1.), (2.,1.)]
        stp_filename (str): the filename used when saving stp files as part of a
            reactor
        color (RGB or RGBA - sequences of 3 or 4 floats, respectively, each in the range 0-1):
            the color to use when exporting as html graphs or png images
        distance (float): the extrusion distance to use (cm units if used for
            neutronics)
        azimuth_placement_angle (float or iterable of floats): the angle or
            angles to use when rotating the shape on the azimuthal axis
        cut (CadQuery object): an optional CadQuery object to perform a boolean
            cut with this object
        material_tag (str): the material name to use when exporting the
            neutronics descrption
        name (str): the legend name used when exporting a html graph of the
            shape
        workplane (str): the orientation of the CadQuery workplane. Options are
            XY, YZ, XZ.

    Returns:
        a paramak shape object: a Shape object that has generic functionality
    """

    def __init__(
        self,
        points,
        distance,
        workplane="XZ",
        stp_filename="ExtrudeSplineShape.stp",
        stl_filename="ExtrudeSplineShape.stl",
        solid=None,
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0,
        cut=None,
        intersect=None,
        union=None,
        material_tag=None,
        name=None,
        **kwargs
    ):

        default_dict = {"tet_mesh": None,
                        "physical_groups": None,
                        "hash_value": None}

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            points=points,
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            workplane=workplane,
            cut=cut,
            intersect=intersect,
            union=union,
            **default_dict
        )

        self.distance = distance
        self.solid = solid

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    def create_solid(self):
        """Creates a 3d solid using points with spline
           edges, azimuth_placement_angle and distance.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # Creates a cadquery solid from points and extrudes
        solid = (
            cq.Workplane(self.workplane)
            .spline(self.points)
            .close()
            .extrude(distance=-1 * self.distance / 2.0, both=True)
        )

        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(
                    solid.rotate(
                        (0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.workplane)

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate(
                (0, 0, -1), (0, 0, 1), self.azimuth_placement_angle)

        self.perform_boolean_operations(solid)

        return solid
