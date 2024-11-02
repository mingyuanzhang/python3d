import trimesh

import numpy as np
import trimesh
from shapely.geometry import Polygon


def validate_and_repair_mesh(mesh):
    """
    Validate and repair the given mesh.
    
    Parameters:
        mesh (trimesh.Trimesh): The input mesh.
    
    Returns:
        trimesh.Trimesh: The validated and repaired mesh.
    """
    # Check for watertightness and other issues
    print("Initial Mesh Validation:")
    print(f"Is the mesh watertight? {mesh.is_watertight}")
    print(f"Number of faces: {len(mesh.faces)}")
    print(f"Number of vertices: {len(mesh.vertices)}")
    
    # Repair the mesh
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fix_inversion(mesh)
    trimesh.repair.fix_winding(mesh)

    # Check for watertightness
    is_watertight = mesh.is_watertight
    print(f"Is the mesh watertight after repair? {is_watertight}")
    
    if not is_watertight:
        # Fill holes
        mesh.fill_holes()
        # Merge vertices to remove duplicates
        mesh.merge_vertices()

    # Check if the mesh is watertight again
    print(f"Is the mesh watertight after filling holes? {mesh.is_watertight}")
    return mesh

def create_threaded_cylinder(radius, height, thread_thickness, thread_pitch):
    """
    Create a threaded cylinder using trimesh, ensuring the mesh is watertight.

    Parameters:
    - radius: Radius of the base cylinder.
    - height: Height of the cylinder.
    - thread_thickness: Thickness of the thread.
    - thread_pitch: The distance between each thread turn.

    Returns:
    - A watertight trimesh mesh object representing the threaded cylinder.
    """
    # Create the base cylinder
    cylinder = trimesh.creation.cylinder(radius=radius+0.1, height=height, sections=64)

    # Define the thread profile (triangle shape with angle pointing outwards)
    # Rotate the triangle so that its point faces radially outwards
    thread_profile = Polygon([
        (0, -thread_pitch / 2),  # Base left
        (0, thread_pitch / 2),   # Base right
        (thread_thickness, 0)        # Tip of the triangle, pointing outwards
    ])

    # Calculate the number of turns the thread will make
    num_turns = (height + thread_pitch/2) / thread_pitch

    # Create the helical path for the thread
    num_steps = int(num_turns * 100)  # Adjust resolution based on number of turns
    t = np.linspace(0, num_turns * 2 * np.pi, num_steps)
    x = (radius + thread_thickness / 3 * 0) * np.cos(t)
    y = (radius + thread_thickness / 3 * 0) * np.sin(t)
    z = (thread_pitch / (2 * np.pi)) * t
    helix_points = np.column_stack((x, y, z))

    # Sweep the thread profile along the helical path
    thread_mesh = trimesh.creation.sweep_polygon(thread_profile, helix_points)

    # Trim the thread to match the cylinder's height
    # top_plane_origin = [0, 0, height]
    # bottom_plane_origin = [0, 0, 0]
    # thread_mesh = thread_mesh.slice_plane(plane_origin=top_plane_origin, plane_normal=[0, 0, -1])
    # thread_mesh = thread_mesh.slice_plane(plane_origin=bottom_plane_origin, plane_normal=[0, 0, 1])

    cutting_box1 = trimesh.creation.box([radius * 10, radius * 10, height*2])
    cutting_box1 = cutting_box1.apply_translation([0, 0, -height])
    cutting_box2 = trimesh.creation.box([radius * 10, radius * 10, height*2])
    cutting_box2 = cutting_box2.apply_translation([0, 0, height+height])

    # cutting_box1.show()

    # Ensure both meshes are watertight before boolean operation
    cylinder.apply_translation([0, 0, height/2])
    cylinder.merge_vertices()
    thread_mesh.merge_vertices()

    # print(thread_mesh.is_watertight)
    # print(cylinder.is_watertight)

    # Perform boolean union to create a single, watertight mesh
    threaded_cylinder = trimesh.boolean.union([cylinder, thread_mesh])
    # threaded_cylinder = validate_and_repair_mesh(threaded_cylinder)
    # threaded_cylinder.show()
    # threaded_cylinder.remove_degenerate_faces()

    # print(threaded_cylinder.is_watertight)

    threaded_cylinder = threaded_cylinder.difference(cutting_box2)
    # threaded_cylinder.show()
    threaded_cylinder = threaded_cylinder.difference(cutting_box1)

    # threaded_cylinder.show()

    # Check if the resulting mesh is watertight
    if not threaded_cylinder.is_watertight:
        print("Warning: The resulting mesh is not watertight.")
    else:
        print("Success: The resulting mesh is watertight.")

    return threaded_cylinder

def flip_z(mesh):
    flip_z_matrix = np.array([
        [1, 0, 0, 0],  # x remains the same
        [0, 1, 0, 0],  # y remains the same
        [0, 0, -1, 0],  # z is negated (flipped)
        [0, 0, 0, 1]   # homogeneous coordinate (no translation)
    ])
    max_z = mesh.bounds[1][2]
    # Apply the transformation to flip the mesh along the z-axis
    mesh.apply_transform(flip_z_matrix)    
    mesh = mesh.apply_translation([0, 0, max_z])
    return mesh

# Example usage
if __name__ == "__main__":
    case_mesh = connector = trimesh.load("iPhone_131_Case.stl")

    #print(case_mesh.bounds)
    case_mesh = case_mesh.apply_translation([0, 0, case_mesh.bounds[0][2]*(-1)])

    radius = 25.0            # Radius of the cylinder
    height = 3.5           # Height of the cylinder
    thread_thickness = 1.5  # Thickness of the thread
    thread_pitch = 2      # Distance between thread peaks

    # Create the threaded cylinder
    threaded_cylinder = create_threaded_cylinder(radius, height, thread_thickness, thread_pitch)
    threaded_cylinder = flip_z(threaded_cylinder)
    threaded_cylinder_cutout = create_threaded_cylinder(radius+0.5, height, thread_thickness, thread_pitch)
    threaded_cylinder_cutout = flip_z(threaded_cylinder_cutout)

    # Visualize the mesh (requires pyglet or other 3D viewer support)
    # threaded_cylinder.show()

    # case = case_mesh.difference(threaded_cylinder)
    # case.show()

    cylinder = trimesh.creation.cylinder(radius=radius * 1.3, height=height, sections=64)
    cylinder = cylinder.apply_translation([0, 0, height/2])
    cylinder = cylinder.difference(threaded_cylinder_cutout)
    # cylinder.show()


    threaded_cylinder.export("~/Downloads/thread.stl")
    cylinder.export("~/Downloads/thread2.stl")