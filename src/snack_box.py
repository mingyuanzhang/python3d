import trimesh
import numpy as np

from threaded_cylinder import create_threaded_cylinder, flip_z
import text3d_utils

tolerance = 0.5

def inch_to_mm(x):
    return x * 25.4

def create_plain_threaded_bottom(inner_radius=inch_to_mm(1.5), height=inch_to_mm(2.5), thread_height=5, wall_thickness=5):
    outer_cylinder = trimesh.creation.cylinder(inner_radius + wall_thickness, height+wall_thickness+thread_height)
    outer_cylinder = outer_cylinder.apply_translation([0, 0, (height+wall_thickness+thread_height)/2])

    inner_cylinder = trimesh.creation.cylinder(inner_radius, height+thread_height)
    inner_cylinder = inner_cylinder.apply_translation([0, 0, (height+thread_height)/2 + wall_thickness])

    plain_bottom = outer_cylinder.difference(inner_cylinder)

    threads_cut = create_threaded_cylinder(inner_radius+tolerance, thread_height, 1.5, 2)
    threads_cut = threads_cut.apply_translation([0, 0, height+wall_thickness])    

    bottom = plain_bottom.difference(threads_cut)

    return bottom

def create_plain_threaded_cap(inner_radius=inch_to_mm(1.5), thread_height=5, wall_thickness=5):
    top_cap = trimesh.creation.cylinder(inner_radius + wall_thickness, wall_thickness)
    top_cap = top_cap.apply_translation([0, 0, wall_thickness/2])

    threads = create_threaded_cylinder(inner_radius, thread_height, 1.5, 2)
    threads = threads.apply_translation([0, 0, wall_thickness])

    cap = trimesh.boolean.union([top_cap, threads])
    cap = flip_z(cap)
    return cap

def add_text_to_bottom(text_string, text_size, text_height, outer_radius, text_pos, bottom_mesh):
    text = text3d_utils.text_3d(text_string, text_size, text_height)
    text_mesh = text3d_utils.text_3d_mesh(text, text_height)
    curved_mesh = text3d_utils.curve_mesh_onto_cylinder_along_z(text_mesh, outer_radius)
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.pi / 2,         # 90 degrees in radians
        direction=[1, 0, 0],     # Rotation around the y-axis
        point=[0, 0, 0]          # Optional: rotation around the origin
    )
    # Apply the rotation to the mesh
    curved_mesh.apply_transform(rotation_matrix)
    curved_mesh.apply_translation([0, 0, text_pos])
    bottom = bottom_mesh.union(curved_mesh)
    return bottom

def cut_cap_for_better_grip(cut_thickness, cut_height, cut_num, outer_radius, cap_mesh):
    cut_cylinder = trimesh.creation.cylinder(cut_thickness/2, cut_height)
    cut_cylinder = cut_cylinder.apply_translation([0, 0, cut_height/2])

    delta_angle = np.pi * 2 / cut_num
    for ii in range(cut_num):
        x_pos = outer_radius * np.cos(ii * delta_angle)
        y_pos = outer_radius * np.sin(ii * delta_angle)
        cut = cut_cylinder.copy()
        cut = cut.apply_translation([x_pos, y_pos, 0])
        cap_mesh = cap_mesh.difference(cut)
    return cap_mesh

def cut_bottom_for_better_grip(cut_thickness, cut_layers, cut_num, outer_radius, bottom_height, bottom_mesh):
    cut_box = trimesh.creation.box([cut_thickness, cut_thickness, cut_thickness])
    cut_box = cut_box.apply_translation([0, 0, cut_thickness/2])

    delta_angle = np.pi * 2 / cut_num
    off_set_angle = delta_angle / 2
    for jj in range(cut_layers):
        z_pos = bottom_height - cut_thickness - jj * cut_thickness
        offset = off_set_angle * jj
        for ii in range(cut_num):
            x_pos = outer_radius * np.cos(ii * delta_angle + offset)
            y_pos = outer_radius * np.sin(ii * delta_angle + offset)
            cut = cut_box.copy()
            cut = cut.apply_translation([x_pos, y_pos, z_pos])
            bottom_mesh = bottom_mesh.difference(cut)
    return bottom_mesh


if __name__ == "__main__":
    box_inner_radius = inch_to_mm(1.5)
    box_inner_height = inch_to_mm(2.5)
    thread_height = 6
    wall_thickness = 5

    bottom = create_plain_threaded_bottom(box_inner_radius, box_inner_height, thread_height, wall_thickness)
    # bottom.show()

    text_string = "MY Snack"
    text_size = 10
    text_height = 2
    outer_radius = box_inner_radius + wall_thickness
    text_pos = box_inner_height * 0.7
    bottom = add_text_to_bottom(text_string, text_size, text_height, outer_radius, text_pos, bottom)
    # bottom.show()
    grip_cut_thickness = 2
    grip_cut_layers = 5
    grip_cut_num = 64
    bottom = cut_bottom_for_better_grip(grip_cut_thickness, grip_cut_layers, grip_cut_num, outer_radius, box_inner_height+wall_thickness+thread_height, bottom)
    # bottom.show()

    cap = create_plain_threaded_cap(box_inner_radius, thread_height, wall_thickness)
    # cap.show()
    grip_cut_thickness = 1
    grip_cut_height = thread_height + wall_thickness
    cut_num = 32
    cap = cut_cap_for_better_grip(grip_cut_thickness, grip_cut_height, cut_num, outer_radius, cap)


    bottom.export("~/Downloads/snack_box_bottom.stl")
    cap.export("~/Downloads/snack_box_cap.stl")
    

