import trimesh
from trimesh.creation import box
from solid import text, linear_extrude, scad_render
import os
import subprocess
from shapely.geometry import Polygon, MultiLineString
from shapely.affinity import rotate as shapely_rotate, translate as shapely_translate
import matplotlib.pyplot as plt
from matplotlib import font_manager
from trimesh.creation import extrude_polygon
import numpy as np

# Define the output directory
output_dir = os.path.expanduser('~/Downloads/')

# Text and board parameters
text_string = "Luke Skywalker"
font_size = 10  # Font size
text_height = 1  # Height of the text
sign_borders = 3
board_thickness = 2

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

# Function to generate text as 3D geometry using OpenSCAD
def text_3d(text_string, size, height):
    return linear_extrude(height=height)(text(text_string, size=size, valign="center", halign="center"))

# Generate the text geometry
text_geom = text_3d(text_string, font_size, text_height)

# Render the text geometry to an OpenSCAD string
scad_code = scad_render(text_geom)

# Path for the OpenSCAD file
scad_path = os.path.join(output_dir, 'text.scad')

# Write the OpenSCAD string to a file
with open(scad_path, 'w') as f:
    f.write(scad_code)

# Convert the OpenSCAD file to STL using OpenSCAD command line
stl_path_text = os.path.join(output_dir, 'text.stl')
subprocess.run(['openscad', '-o', stl_path_text, scad_path])

# Load the text geometry from the generated STL file
text_mesh = trimesh.load_mesh(stl_path_text)

# Center the text on the board
text_bounds = text_mesh.bounding_box.extents
text_translation = [
    0,
    0,
    board_thickness / 2
]
text_mesh.apply_translation(text_translation)

# Create the board
board = box(extents=[text_bounds[0] + 8 * sign_borders, text_bounds[1] + 2 * sign_borders, board_thickness])


# Combine the board and the text
model = board.union(text_mesh)

key_ring = create_key_ring_loop(
        inner_radius=2,  # Slightly larger than the knob radius
        tube_radius=1,
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
        board.bounds[0][0] - key_ring.extents[0] / 2 + 1,  # Slightly beyond the knob
        0,
        0
    ])

model = model.union(key_ring)

# model.show()
# Path for the output STL file
stl_path = os.path.join(output_dir, 'text_on_board_keychain.stl')

# Export to STL
model.export(stl_path)
