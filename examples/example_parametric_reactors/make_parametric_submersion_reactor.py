"""
This example creates a submersion ball reactor using the SubmersionTokamak
parametric shape
"""

import paramak


def main():

    my_reactor = paramak.SubmersionTokamak(
        inner_bore_radial_thickness=30,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=30,
        divertor_radial_thickness=80,
        inner_plasma_gap_radial_thickness=50,
        plasma_radial_thickness=200,
        outer_plasma_gap_radial_thickness=50,
        firstwall_radial_thickness=30,
        blanket_rear_wall_radial_thickness=30,
        number_of_tf_coils=16,
        rotation_angle=180,
        support_radial_thickness=50,
        inboard_blanket_radial_thickness=30,
        outboard_blanket_radial_thickness=30,
        plasma_high_point=(200, 150),
        pf_coil_radial_thicknesses=[30, 30, 30, 30],
        pf_coil_vertical_thicknesses=[30, 30, 30, 30],
        pf_coil_to_tf_coil_radial_gap=50,
        outboard_tf_coil_radial_thickness=30,
        outboard_tf_coil_poloidal_thickness=30,
        tf_coil_to_rear_blanket_radial_gap=20,
    )

    my_reactor.export_stp()

    my_reactor.export_neutronics_description()


if __name__ == "__main__":
    main()
