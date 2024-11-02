import trimesh
import numpy as np


def fabric_piece(square_side_length, thickness, inner_radius, tolerance=0.5):
    square = trimesh.creation.box([square_side_length, square_side_length, thickness])

    k = square_side_length / 10
    outer_radius = thickness / 2    

    def make_connector():
        base = trimesh.creation.box([thickness, thickness / 2 + tolerance , k - tolerance])
        cylinder1 = trimesh.creation.cylinder(radius=outer_radius, height=k-tolerance)
        cylinder1 = cylinder1.apply_translation([0, outer_radius/2+ tolerance, 0])
        connector = base.union(cylinder1)
        cylinder2 = trimesh.creation.cylinder(radius=inner_radius+tolerance, height=k-tolerance)
        cylinder2 = cylinder2.apply_translation([0, outer_radius/2+ tolerance, 0])
        connector = connector.difference(cylinder2)  
        return connector

    ## top
    connector = make_connector()
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [0, 1, 0]        # Rotation axis (x-axis)
    )
    # Apply the rotation
    connector.apply_transform(rotation_matrix)         
    connector1 = connector.copy()
    connector1 = connector1.apply_translation([k/2 * (-1), square_side_length/2+outer_radius/2+tolerance/2, 0])        
    connector2 = connector.copy()
    connector2 = connector2.apply_translation([k * 3 / 2 * (1), square_side_length/2+outer_radius/2+tolerance/2, 0])  
    connector_combo = trimesh.boolean.union([connector1, connector2])

    connector_combo1 = connector_combo.copy()
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [0, 0, 1]        # Rotation axis (x-axis)
    )    
    connector_combo1.apply_transform(rotation_matrix)

    connector_combo2 = connector_combo1.copy()
    connector_combo2.apply_transform(rotation_matrix)

    connector_combo3 = connector_combo2.copy()
    connector_combo3.apply_transform(rotation_matrix)

    mesh = trimesh.boolean.union([square,connector_combo, connector_combo1, connector_combo2, connector_combo3])

    return mesh


def fabric_connecting_rod(square_side_length, inner_radius, thickness, tolerance=0.5):
    k = square_side_length / 10
    end_radius = thickness / 2
    cylinder1 = trimesh.creation.cylinder(radius=inner_radius, height=k * 4+tolerance*2)
    cylinder2 = trimesh.creation.cylinder(radius=end_radius-tolerance, height = k)
    cylinder3 = trimesh.creation.cylinder(radius=end_radius-tolerance, height = k)
    cylinder2 = cylinder2.apply_translation([0, 0, k*2+k/2+tolerance])
    cylinder3 = cylinder3.apply_translation([0, 0, -1 * (k*2+k/2+tolerance)])
    rod =  trimesh.boolean.union([cylinder1, cylinder2, cylinder3])
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [0, 1, 0]        # Rotation axis (x-axis)
    )    
    rod.apply_transform(rotation_matrix)    
    return rod


if __name__ == "__main__":
    square_side_length = 20
    thickness = 6
    inner_radius = 1.5
    tolerance = 0.5

    x_size = 4
    y_size = 4

    piece = fabric_piece(square_side_length, thickness, inner_radius, tolerance)
    pieces = []
    for ii in range(x_size):
        for jj in range(y_size):
            x_pos = ii * (square_side_length + thickness + tolerance*2)
            y_pos = jj * (square_side_length + thickness + tolerance*2)
            new_piece = piece.copy()
            new_piece = new_piece.apply_translation([x_pos, y_pos, 0])
            pieces.append(new_piece)
    fabric = trimesh.boolean.union(pieces)
    print(fabric.is_volume)
    # fabric.show()

    rod = fabric_connecting_rod(square_side_length, inner_radius, thickness, tolerance)
    rod_rotate = rod.copy()
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [0, 0, 1]        # Rotation axis (x-axis)
    )    
    rod_rotate.apply_transform(rotation_matrix)    

    rods = []
    for ii in range(x_size):
        for jj in range(y_size-1):
            x_pos = ii * (square_side_length + thickness+ tolerance*2) 
            y_pos = jj * (square_side_length + thickness+ tolerance*2) + ((square_side_length + thickness+ tolerance*2)/2)
            new_rod = rod.copy()
            new_rod = new_rod.apply_translation([x_pos, y_pos, 0])
            rods.append(new_rod)
    for ii in range(x_size-1):
        for jj in range(y_size):
            x_pos = ii * (square_side_length + thickness+ tolerance*2) + ((square_side_length + thickness+ tolerance*2)/2)
            y_pos = jj * (square_side_length + thickness+ tolerance*2) 
            new_rod = rod_rotate.copy()
            new_rod = new_rod.apply_translation([x_pos, y_pos, 0])
            rods.append(new_rod)                   
    all_rods = trimesh.boolean.union(rods)    
    print(all_rods.is_volume)
    # all_rods.show()

    mesh = trimesh.util.concatenate([fabric, all_rods])
    # mesh.show()
    mesh.export("~/Downloads/fabric_test.stl")