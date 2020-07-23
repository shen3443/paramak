
import os
import unittest
from pathlib import Path

import pytest

from paramak import SweepStraightShape


class test_object_properties(unittest.TestCase):
    def test_simple_solid_constuction(self):
        """checks that a simple swept solid can be created"""

        test_shape = SweepStraightShape(
            points = [
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points = [
                (50, 0),
                (20, 200),
                (50, 400)
            ],
            workplane = "XY",
            path_workplane = "XZ"
        )

        test_shape.create_solid()
        
        assert test_shape.solid is not None

    def test_relative_shape_volumes_faces(self):
        """creates two shapes with different face shapes and checks that their relative
                volumes are correct"""

        test_shape_1 = SweepStraightShape(
            points = [
                (-10, 10),
                (10, 10),
                (10, -10),
                (-10, -10)
            ],
            path_points = [
                (50, 0),
                (20, 200),
                (50, 400)
            ],
            workplane = "XY",
            path_workplane = "XZ"
        )

        test_shape_2 = SweepStraightShape(
            points = [
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points = [
                (50, 0),
                (20, 200),
                (50, 400)
            ],
            workplane = "XY",
            path_workplane = "XZ"
        )

        assert test_shape_2.volume == pytest.approx(test_shape_1.volume * 4)

    def test_relative_shape_volumes_splines(self):
        """creates two shapes with the same face but sweeps along different splines and
                checks that their relative volumes are correct"""

        test_shape_1 = SweepStraightShape(
            points = [
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points = [
                (100, 0),
                (75, 100),
                (50, 200),
                (50, 300),
                (50, 400),
                (75, 500),
                (100, 600)
            ],
            workplane = "XY",
            path_workplane = "XZ"
        )

        test_shape_2 = SweepStraightShape(
            points = [
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points = [
                (100, 0),
                (75, 100),
                (50, 200),
                (50, 300)
            ],
            workplane = "XY",
            path_workplane = "XZ"
        )

        assert test_shape_1.volume == pytest.approx(test_shape_2.volume * 2, rel=0.01)   # within 1%


    def test_cut_volume(self):
        """creates two swept shapes and cuts one from the other and checks that the volume
                is correct"""

        inner_shape = SweepStraightShape(
            points = [
                (-10, 10),
                (10, 10),
                (10, -10),
                (-10, -10)
            ],
            path_points = [
                (100, 0),
                (75, 100),
                (50, 200),
                (75, 300),
                (100, 400)
            ],
            workplane = "XY",
            path_workplane = "XZ"
        )

        outer_shape = SweepStraightShape(
            points = [
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points = [
                (100, 0),
                (75, 100),
                (50, 200),
                (75, 300),
                (100, 400)
            ],
            workplane = "XY",
            path_workplane = "XZ"
        )

        outer_shape_with_cut = SweepStraightShape(
            points = [
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points = [
                (100, 0),
                (75, 100),
                (50, 200),
                (75, 300),
                (100, 400)
            ],
            workplane = "XY",
            path_workplane = "XZ",
            cut = inner_shape
        )

        assert outer_shape_with_cut.volume == pytest.approx(outer_shape.volume - inner_shape.volume)


    def test_errors_raised_when_workplane_and_path_workplane_not_relatively_correct(self):
        """tries to create a shape with workplane = path_workplane and checks that an 
                error is correctly raised"""

        with pytest.raises(ValueError) as exe_info:
            shape = SweepStraightShape(
                points = [
                    (-10, 10), (10, 10), (10, -10), (-10, -10)
                ],
                path_points = [
                    (50, 0), (0, 200), (50, 400)
                ],
                workplane = "XY",
                path_workplane = "XY"
            )
    



        