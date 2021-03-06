import pytest
import paramak
import unittest


class test_InnerTfCoilsCircular(unittest.TestCase):
    def test_InnerTfCoilsCircular_creation(self):
        """creates an inner tf coil using the InnerTfCoilsCircular parametric component and checks
        that a cadquery solid is created"""

        test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_InnerTfCoilsCircular_azimuth_offset(self):
        """creates an inner tf coil using the InnerTfCoilsCircular parametric component and checks
        that the azimuthal start angle can be changed correctly"""

        test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )

        assert test_shape.azimuth_placement_angle == [
            0, 60, 120, 180, 240, 300]
        test_shape.azimuth_start_angle = 20
        assert test_shape.azimuth_placement_angle == [
            20, 80, 140, 200, 260, 320]