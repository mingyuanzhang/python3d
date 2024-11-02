import trimesh
import numpy as np
from shapely.geometry import Polygon, MultiLineString
from shapely.affinity import rotate as shapely_rotate, translate as shapely_translate
import matplotlib.pyplot as plt
from matplotlib import font_manager
from trimesh.creation import extrude_polygon


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
        mesh = mesh.fill_holes()
        # Merge vertices to remove duplicates
        mesh.merge_vertices()

    # Check if the mesh is watertight again
    print(f"Is the mesh watertight after filling holes? {mesh.is_watertight}")
    return mesh

def create_text_mesh(text, font_size=1.0, depth=0.2):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from matplotlib.path import Path
    import shapely.geometry as sg
    from trimesh.creation import extrude_polygon
    import trimesh

    # Create a TextPath object
    fp = FontProperties(family="DejaVu Sans", size=font_size)
    text_path = TextPath((0, 0), text, prop=fp)

    # Get the vertices and codes from the TextPath
    vertices = text_path.vertices
    codes = text_path.codes

    # Create a Path object
    path = Path(vertices, codes)

    # Convert the Path to Shapely Polygons
    polygons = []
    for polygon in path.to_polygons():
        if len(polygon) >= 3:  # Valid polygon must have at least 3 points
            poly = sg.Polygon(polygon)
            if poly.is_valid and not poly.is_empty:
                polygons.append(poly)

    # Extrude each polygon separately and collect the meshes
    meshes = []
    for poly in polygons:
        # Extrude the polygon to create a mesh
        extruded = extrude_polygon(poly, height=depth)
        meshes.append(extruded)

    # Combine all the extruded meshes into one mesh
    if len(meshes) > 1:
        text_mesh = trimesh.util.concatenate(meshes)
    else:
        text_mesh = meshes[0]

    # text_mesh.show()
    return validate_and_repair_mesh(text_mesh)



def map_text_onto_barrel(text_mesh, barrel_radius, barrel_start, barrel_end):
    # Flatten the text mesh onto the XZ-plane (text reads along X-axis)
    text_mesh.apply_translation(-text_mesh.centroid)
    
    # Scale text to fit the barrel length
    text_length = text_mesh.extents[0]
    barrel_length = barrel_end - barrel_start
    scale_factor = barrel_length / text_length
    text_mesh.apply_scale([scale_factor, 1, 1])  # Scale along X-axis only
    
    # Move text to the desired position along the bat
    text_mesh.apply_translation([barrel_start + barrel_length / 2, 0, 0])
    
    # Map text onto barrel surface
    vertices = text_mesh.vertices
    x = vertices[:, 0]  # Along the bat's length
    y = vertices[:, 1]  # Across the text (height of letters)
    z = vertices[:, 2]  # Depth of the text (extrusion)
    
    # Adjust angular range (e.g., mapping over 90 degrees)
    angular_range = np.radians(90)  # Adjust angular range as needed

    # Map y-coordinate onto angle around the barrel
    theta = -(y / text_mesh.extents[1]) * angular_range + angular_range / 2

    # New coordinates on barrel surface
    new_x = x
    new_y = barrel_radius * np.cos(theta)
    new_z = barrel_radius * np.sin(theta)
    
    # Update vertices
    text_mesh.vertices = np.column_stack((new_x, new_y, new_z))
    
    return text_mesh


def add_text_to_bat(bat, text, barrel_radius, barrel_length_start, barrel_length_end):
    # Create the text mesh
    text_mesh = create_text_mesh(text, font_size=0.8, depth=0.04)

    # Map the text onto the barrel
    text_mesh = map_text_onto_barrel(text_mesh, barrel_radius, barrel_length_start, barrel_length_end)
    # text_mesh.show()
    # text_mesh.apply_transform(
    #     trimesh.transformations.rotation_matrix(
    #         angle=np.radians(90),
    #         direction=[0, 1, 0],  # Rotate around Y-axis
    #         point=bat.centroid
    #     )
    # )

    # Since we want the text to appear as if printed on the barrel, we can simply combine the meshes
    bat_with_text = trimesh.util.concatenate([bat, text_mesh])

    return bat_with_text

# Create the baseball bat
def create_baseball_bat():
    # Define the parameters of the bat
    total_length = 39.0  # Total length of the bat
    handle_length = 15.0  # Length of the handle
    mid_barrel_length = 10.0
    knob_radius = 1.0  # Radius of the knob at the end of the handle
    handle_radius = 0.8  # Radius of the handle
    barrel_radius = 2.5  # Maximum radius of the barrel
    tip_length = 0.5  # Length of the rounded tip at the end of the barrel

    # Create the profile of the bat in the XY-plane (X: radius, Y: length)
    profile_points = np.array([
        # Knob
        [0.0, 0.0],                      # Point 0: Start at knob center
        [knob_radius, 0.0],
        [knob_radius, 0.2],              # Point 1: Knob outer edge
        [handle_radius, 0.4],            # Point 2: Transition to handle

        # Handle
        [handle_radius, handle_length],  # Point 3: End of handle

        # Barrel taper
        [handle_radius + 0.5, handle_length + 2.0],          # Point 4: Start of barrel taper
        [barrel_radius - 0.5, handle_length + mid_barrel_length],          # Point 5: Mid barrel
        # [barrel_radius, handle_length + mid_barrel_length],          # Point 5: Mid barrel
        [barrel_radius, total_length - tip_length],          # Point 6: End of barrel before tip

        # Barrel tip
        [barrel_radius - 0.2, total_length],                 # Point 7: Start of tip taper
        [0.0, total_length + tip_length],                    # Point 8: Tip end point
    ])

    # Use revolve to create the bat mesh
    bat = trimesh.creation.revolve(
        profile_points,          # Pass profile_points as positional argument 'linestring'
        angle=2 * np.pi,         # Full 360 degrees
        axis=[0, 1, 0],          # Revolve around Y-axis
        point=[0, 0, 0],
        angle_resolution=64      # Increase for smoother surface
    )

    # Rotate the bat to align along the X-axis
    bat.apply_transform(
        trimesh.transformations.rotation_matrix(
            angle=np.radians(90),
            direction=[0, 1, 0],  # Rotate around Y-axis
            point=bat.centroid
        )
    )

    # Center the bat at the origin
    bat.apply_translation(-bat.centroid)

    return bat

# Create the baseball
def create_baseball():
    # Dimensions
    ball_radius = 2

    # Create the sphere
    ball = trimesh.creation.icosphere(subdivisions=3, radius=ball_radius)

    # Position the ball near the bat
    ball.apply_translation([5, 5, 0])

    return ball

# Create the baseball glove
def create_baseball_glove():
    # Approximate the glove as an extruded 2D shape
    # Define the glove outline using 2D points
    glove_outline = np.array([
        [-1.5, 0],
        [-1.2, 0.5],
        [-0.8, 0.8],
        [0, 1],
        [0.8, 0.8],
        [1.2, 0.5],
        [1.5, 0],
        [1.2, -0.5],
        [0.8, -0.8],
        [0, -1],
        [-0.8, -0.8],
        [-1.2, -0.5],
        [-1.5, 0]
    ])

    # Create a polygon from the outline
    glove_polygon = Polygon(glove_outline)

    # Extrude the polygon to create a 3D object
    glove = trimesh.creation.extrude_polygon(glove_polygon, height=0.3)
    glove.apply_translation([3, 0, 0.15])

    return glove

def create_key_ring_loop(inner_radius=1.2, tube_radius=0.1, segments=64):
    """
    Create a key ring loop (torus) to attach to the bat.

    Parameters:
    - inner_radius: The distance from the center of the torus to the center of the tube.
    - tube_radius: The radius of the tube.
    - segments: The number of segments for the torus mesh.

    Returns:
    - A Trimesh object representing the key ring loop.
    """
    # Create the torus (ring)
    key_ring = trimesh.creation.torus(
        # sections=segments,
        sections_minor=segments // 2,
        major_radius=inner_radius,
        minor_radius=tube_radius
    )
    return key_ring

def create_bat_with_key_ring():
    bat = create_baseball_bat()

    # Get the position at the end of the knob
    knob_length = 0.4
    knob_radius = 1.0

    # Position where the knob ends (after rotation)
    knob_end_x = bat.bounds[0][0]  # Since bat is along X-axis

    # Create the key ring loop
    key_ring = create_key_ring_loop(
        inner_radius=knob_radius + 0.1,  # Slightly larger than the knob radius
        tube_radius=0.25,
        segments=64
    )

    # Align the key ring loop perpendicular to the bat
    key_ring.apply_transform(
        trimesh.transformations.rotation_matrix(
            angle=np.radians(90),
            direction=[0, 0, 1],
            point=[0, 0, 0]
        )
    )

    # Position the key ring loop at the end of the knob
    key_ring.apply_translation([
        knob_end_x - key_ring.extents[0] / 2 + 0.5,  # Slightly beyond the knob
        0,
        0
    ])

    # Combine the bat and key ring loop
    bat_with_key_ring = trimesh.util.concatenate([bat, key_ring])

    # Export the bat with key ring to an STL file
    bat_with_key_ring.export('~/Downloads/baseball_bat_with_key_ring.stl')

    # Optionally, visualize the bat
    # bat_with_key_ring.show()


# Main function to create the keychain ornament
def create_keychain_ornament():
    bat = create_baseball_bat()
    ball = create_baseball()
    # glove = create_baseball_glove()
    # loop = create_keyring_loop()

    # text = "Cat X"  # Replace with your desired text

    # bat = add_text_to_bat(bat, text, 2.5, 26 - 39/2-5., 38 - 39.0/2-6)

    # Combine all parts into one mesh
    # ornament = trimesh.util.concatenate([bat, ball, glove, loop])
    ornament = trimesh.util.concatenate([bat, ball])

    # Export to STL
    ornament.export('~/Downloads/baseball_keychain_ornament.stl')

    # Optionally, show the model
    # ornament.show()

# Run the main function
if __name__ == "__main__":
    # create_keychain_ornament()
    create_bat_with_key_ring()