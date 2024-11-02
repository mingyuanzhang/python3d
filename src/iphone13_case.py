import trimesh

import numpy as np
import trimesh
from shapely.geometry import Polygon

from threaded_cylinder import create_threaded_cylinder, flip_z

from text3d_utils import text_3d, text_3d_mesh
from utils import slice_plane_x, validate_and_repair_mesh, scale_mesh
from baseball_themed_keychain import create_baseball_bat
from image3d_simple import image_to_3d_model, image_utils, create_extruded_mesh

import os

# Example usage
if __name__ == "__main__":
    # case_mesh = connector = trimesh.load("stls/iPhone_131_Case.stl")
    case_mesh = connector = trimesh.load("../stls/Iphone13_case_tpu.stl")
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(90),  # 90 degrees
        direction=[1, 0, 0],   # Rotation around the X-axis
        point=[0, 0, 0]        # Rotate around the origin
    )
    case_mesh = case_mesh.apply_transform(rotation_matrix)

    #print(case_mesh.bounds)
    case_mesh = case_mesh.apply_translation([0, 0, case_mesh.bounds[0][2]*(-1)])
    # print(case_mesh.bounds)
    # case_mesh.show()
    # exit(0)

    ##patch for tpu
    box = trimesh.creation.box([50, 50, 2])
    box = box.apply_translation([0, 0, 2/2])
    case_mesh = case_mesh.union(box)

    another_big_box = trimesh.creation.box([1000, 1000, 50])
    another_big_box = another_big_box.apply_translation([0, 0, 25 + 2])
    case_bottom = case_mesh.difference(another_big_box)
    # case_bottom.show()
    case_bottom = case_bottom.apply_translation([0, 0, -1.4])
    case_mesh = trimesh.boolean.union([case_mesh, case_bottom])
    case_mesh = case_mesh.apply_translation([0, 0, 1.4])

    # case_mesh.show()

    radius = 25.0            # Radius of the cylinder
    height = 3.5           # Height of the cylinder
    thread_thickness = 1.5  # Thickness of the thread
    thread_pitch = 2      # Distance between thread peaks

    # Create the threaded cylinder
    threaded_cylinder = create_threaded_cylinder(radius, height, thread_thickness, thread_pitch)
    threaded_cylinder = flip_z(threaded_cylinder)
    
    threaded_cylinder_cutout = create_threaded_cylinder(radius+0.2, height, thread_thickness, thread_pitch)    
    threaded_cylinder_cutout = flip_z(threaded_cylinder_cutout)

    # Visualize the mesh (requires pyglet or other 3D viewer support)
    # threaded_cylinder.show()

    threaded_cylinder_cutout.apply_translation([0, -20, 0])
    case = case_mesh.difference(threaded_cylinder_cutout)
    # case.show()

    # cylinder = trimesh.creation.cylinder(radius=radius * 1.3, height=height, sections=64)
    # cylinder = cylinder.apply_translation([0, 0, height/2])
    # cylinder = cylinder.difference(threaded_cylinder)
    # cylinder.show()


    threaded_cylinder.export("~/Downloads/thread.stl")
    case.export("~/Downloads/iphone13_case.stl")

    # text = text_3d_mesh(text_3d("Z", 20, height * 2), 0)
    # threaded_cylinder_text = threaded_cylinder.difference(text)
    # # threaded_cylinder_text.show()
    # threaded_cylinder_text.export("~/Downloads/thread_text.stl")

    # mount = trimesh.load("stls/StraightTwoScrews.stl")
    # mount = slice_plane_x(mount, radius - 5.0, "left")
    # # mount.show()
    # mount = slice_plane_x(mount, -radius+5.0, "right")
    # # mount.show()
    # threaded_cylinder_mount = threaded_cylinder.union(mount)
    # # threaded_cylinder_mount.show()
    # threaded_cylinder_mount.export("~/Downloads/thread_mount.stl")

    # bat = create_baseball_bat()
    # bat = scale_mesh(bat, 2)
    # rotation_matrix = trimesh.transformations.rotation_matrix(
    #     angle=np.radians(90),  # 90 degrees
    #     direction=[0, 1, 0],   # Rotation around the X-axis
    #     point=[0, 0, 0]        # Rotate around the origin
    # )

    # # Apply the rotation matrix to the mesh
    # bat = bat.apply_transform(rotation_matrix)   
    # rotation_matrix = trimesh.transformations.rotation_matrix(
    #     angle=np.radians(180),  # 90 degrees
    #     direction=[0, 0, 1],   # Rotation around the X-axis
    #     point=[0, 0, 0]        # Rotate around the origin
    # )
    # # Apply the rotation matrix to the mesh
    # bat = bat.apply_transform(rotation_matrix)      
    # rotation_matrix = trimesh.transformations.rotation_matrix(
    #     angle=np.radians(180),  # 90 degrees
    #     direction=[0, 1, 0],   # Rotation around the X-axis
    #     point=[0, 0, 0]        # Rotate around the origin
    # )

    # # Apply the rotation matrix to the mesh
    # bat = bat.apply_transform(rotation_matrix)        
    # # print(bat.bounds)
    # bat = bat.apply_translation([0, 0, bat.bounds[0][2] * (-1) + height])
    # threaded_cylinder_bat = threaded_cylinder.union(bat)
    # # threaded_cylinder_bat.show()
    # threaded_cylinder_bat.export("~/Downloads/thread_bat.stl")

