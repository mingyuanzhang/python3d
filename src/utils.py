import trimesh
import numpy as np

def slice_plane_x(mesh, x_coordinate, side="left"):
    big_box = trimesh.creation.box(mesh.bounding_box.extents)
    # print(big_box.bounds)
    # print(mesh.bounds)
    # print(mesh.bounding_box.extents)
    if side == "right":
        big_box_cut = big_box.apply_translation([mesh.bounds[1][0] * (-1) + x_coordinate, 0, mesh.bounds[0][2] - big_box.bounds[0][2]])
    else :
        big_box_cut = big_box.apply_translation([mesh.bounds[0][0] * (-1) + x_coordinate, 0,  mesh.bounds[0][2] - big_box.bounds[0][2]])
    
    return mesh.difference(big_box_cut)



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


def scale_mesh(mesh, factor):
    scaling_factor = factor

    # Create a scaling matrix
    scaling_matrix = np.eye(4) * scaling_factor
    scaling_matrix[3, 3] = 1  # Keep the homogeneous coordinate intact

    # Apply the scaling matrix to the mesh
    mesh.apply_transform(scaling_matrix)    
    return mesh