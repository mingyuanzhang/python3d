import trimesh
import numpy as np

import threaded_cylinder

from hand_bag import create_rounded_rectangle
from threaded_cylinder import create_threaded_cylinder, flip_z


tolerance = 0.5

def inch_to_mm(x):
    return x * 25.4

def create_iphone13_camera_piece(depth=2):
    base_length = inch_to_mm(1.25)
    base_radius = inch_to_mm(1.5/2)
    # base_square = trimesh.creation.box([base_length, base_length, depth])
    # base_cylinder = trimesh.creation.cylinder(radius=base_radius, height=depth, sections=64*64)
    # base_piece = trimesh.boolean.intersection([base_square, base_cylinder])

    base_piece = create_rounded_rectangle(base_length, base_length, base_length/4, depth)
    # base_piece.show()

    camera_radius = inch_to_mm(0.25)
    camera_position = inch_to_mm(0.25) #base_radius / 2 / (2**0.5)
    camera_hole1 = trimesh.creation.cylinder(radius=camera_radius, height=depth)
    camera_hole1 = camera_hole1.apply_translation([camera_position, -camera_position, depth/2])

    camera_hole2 = trimesh.creation.cylinder(radius=camera_radius, height=depth)
    camera_hole2 = camera_hole2.apply_translation([-camera_position, camera_position, depth/2])

    mesh = base_piece.difference(camera_hole1)
    mesh = mesh.difference(camera_hole2)
    return mesh


def create_eye_pieces():
    inner_radius = inch_to_mm(5.25 / 3.1415926 / 2)
    height = inch_to_mm(1.125)
    material_thickness = 3
    tolerance = 0.5

    thread_thickness = 1.5
    thread_pitch = 2

    male_thread_radius = inner_radius + material_thickness
    outer_cylinder_radius = male_thread_radius + material_thickness + thread_thickness

    inner_thread = threaded_cylinder.create_threaded_cylinder(male_thread_radius, height, thread_thickness, thread_pitch)
    inner_cut = trimesh.creation.cylinder(inner_radius, height)
    inner_cut = inner_cut.apply_translation([0, 0, height/2])
    inner_thread = inner_thread.difference(inner_cut)
    # inner_thread.show()

    inner_thread_cut = threaded_cylinder.create_threaded_cylinder(male_thread_radius+tolerance, height/2, thread_thickness, thread_pitch)
    outer_thread = trimesh.creation.cylinder(outer_cylinder_radius, height/2)
    outer_thread = outer_thread.apply_translation([0, 0, height/4])
    outer_thread = outer_thread.difference(inner_thread_cut)    

    return inner_thread, outer_thread

def create_iphone13_attachment(eye_piece_outer, depth=2):
    base_length = inch_to_mm(5.0) + inch_to_mm(0.5)
    base_width = inch_to_mm(2.5) + inch_to_mm(0.5)
    corner_radius = inch_to_mm(1.25) / 4
    base_piece = create_rounded_rectangle(base_length, base_width, corner_radius, depth)

    camera_radius = inch_to_mm(0.25)    
    camera_hole = trimesh.creation.cylinder(radius=camera_radius, height=depth)
    camera_position_x = -inch_to_mm(2.5) + inch_to_mm(1.25)/2 + inch_to_mm(0.25)
    camera_position_y = inch_to_mm(1.25)/2 - inch_to_mm(0.25)
    camera_hole = camera_hole.apply_translation([camera_position_x, camera_position_y, depth/2])
    base_piece = base_piece.difference(camera_hole)
    eye_piece_outer_extents = eye_piece_outer.bounding_box.extents
    eye_piece_outer = eye_piece_outer.apply_translation([camera_position_x, camera_position_y, -eye_piece_outer_extents[2]])
    base_piece = base_piece.union(eye_piece_outer)


    radius = 25.0            # Radius of the cylinder
    height = 3.5           # Height of the cylinder
    thread_thickness = 1.5  # Thickness of the thread
    thread_pitch = 2      # Distance between thread peaks

    # Create the threaded cylinder
    threaded_cylinder = create_threaded_cylinder(radius, height+depth, thread_thickness, thread_pitch)
    threaded_cylinder = flip_z(threaded_cylinder)
    handle = trimesh.creation.cylinder(radius / 3, 10)
    handle = handle.apply_translation([0, 0, (height+depth)/2+5])
    threaded_cylinder = threaded_cylinder.union(handle)
    
    threaded_cylinder_cutout = create_threaded_cylinder(radius+0.2, height, depth, thread_pitch)    
    threaded_cylinder_cutout = flip_z(threaded_cylinder_cutout)    
    threaded_cylinder_cutout = threaded_cylinder_cutout.apply_translation([inch_to_mm(1+3/32), -inch_to_mm(3/32), 0])
    base_piece = base_piece.difference(threaded_cylinder_cutout)

    return base_piece, threaded_cylinder


def create_iphone13_base_piece(eye_piece_outer, depth=2):
    base_length = inch_to_mm(5.0) + inch_to_mm(0.5)
    base_width = inch_to_mm(2.5) + inch_to_mm(0.5)
    corner_radius = inch_to_mm(1.25) / 4
    base_piece = create_rounded_rectangle(base_length, base_width, corner_radius, depth)

    camera_radius = inch_to_mm(0.25)    
    camera_hole = trimesh.creation.cylinder(radius=camera_radius, height=depth)
    camera_position_x = -inch_to_mm(2.5) + inch_to_mm(1.25)/2 + inch_to_mm(0.25)
    camera_position_y = inch_to_mm(1.25)/2 - inch_to_mm(0.25)
    camera_hole = camera_hole.apply_translation([camera_position_x, camera_position_y, depth/2])
    base_piece = base_piece.difference(camera_hole)
    eye_piece_outer_extents = eye_piece_outer.bounding_box.extents
    eye_piece_outer = eye_piece_outer.apply_translation([camera_position_x, camera_position_y, -eye_piece_outer_extents[2]])
    base_piece = base_piece.union(eye_piece_outer)

    base_piece = base_piece.apply_translation([-camera_position_x, -camera_position_y, 0])

    return base_piece

def create_simplified_iphone_case(base_piece, depth=2):
    case_mesh = trimesh.load("../stls/iPhone_131_Case.stl")
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(90),  # 90 degrees
        direction=[0, 0, 1],   # Rotation around the X-axis
        point=[0, 0, 0]        # Rotate around the origin
    )
    case_mesh = case_mesh.apply_transform(rotation_matrix)

    box_cut = trimesh.creation.box([inch_to_mm(4), inch_to_mm(8), 20])
    box_cut = box_cut.apply_translation([0, 0, 10+2])
    case_mesh = case_mesh.difference(box_cut)
    # case_mesh.show()

    x_pos = -inch_to_mm(2 + 2.7/32) + inch_to_mm(0.25)
    y_pos = inch_to_mm(0.75 - 1/32) - inch_to_mm(0.25)
    base_piece = base_piece.apply_translation([x_pos, y_pos, -depth])

    mesh = trimesh.boolean.union([case_mesh, base_piece])
    return mesh


if __name__ == "__main__":
    eye_piece_inner, eye_piece_outer = create_eye_pieces()

    # iphone_attachement, connector = create_iphone13_attachment(eye_piece_outer, depth=2)
    # # connector.show()
    eye_piece_inner.export("~/Downloads/binocular_phonemount_eye_piece_inner.stl")
    # iphone_attachement.export("~/Downloads/binocular_phonemount_iphone13_attachment.stl")
    # connector.export("~/Downloads/binocular_phonemount_iphone13_connector.stl")
    iphone_base_piece = create_iphone13_base_piece(eye_piece_outer, depth=2)
    mesh = create_simplified_iphone_case(iphone_base_piece, depth=4.2)
    # mesh.show()
    mesh.export("~/Downloads/binocular_phonemount_iphone_case.stl")