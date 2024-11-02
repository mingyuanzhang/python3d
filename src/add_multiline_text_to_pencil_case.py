import trimesh
from trimesh.creation import box
from solid import text, linear_extrude, scad_render
import os
import subprocess
import numpy as np
from solid.utils import translate


def center_mesh(mesh):
    # Get the bounding box
    bbox_min, bbox_max = mesh.bounds
    
    # Calculate the center of the bounding box
    center = (bbox_min + bbox_max) / 2
    
    # Translate the mesh by the negative center to move it to (0, 0, 0)
    mesh.apply_translation(-center)
    
    return mesh

def curve_mesh_onto_cylinder(mesh, radius):
    mesh = center_mesh(mesh)
    for vertex in mesh.vertices:
        # Get the original x, y, z coordinates
        x, y, z = vertex

        # Convert x (linear distance) to an angular displacement around the cylinder
        angle = y / radius

        # Map the flat vertex onto the curved surface
        new_z = radius * np.cos(angle) + z*0.5

        # Set the new vertex position
        vertex[2] = new_z
    
    return mesh


def multi_line_text(text_lines, line_spacing=10, size=10, height=5):
    lines = []
    for i, line in enumerate(text_lines):
        # Position each line by translating it down based on the line number
        lines.append(translate([0, -i * line_spacing, 0])(text(line, size=size, halign="center", valign="center")))
    return linear_extrude(height=height)(lines)

# Define the output directory
output_dir = os.path.expanduser('~/Downloads/')

# Text and board parameters
text_string = """
Shall I compare thee to a summer’s day?
Thou art more lovely and more temperate.
Rough winds do shake the darling buds of May,
And summer’s lease hath all too short a date.
"""
font_size = 5  # Font size
line_spacing = font_size+1
text_height = 2  # Height of the text
board_thickness = 2

# Function to generate text as 3D geometry using OpenSCAD
def text_3d(text_string, size, height):
    return linear_extrude(height=height)(text(text_string, size=size, valign="center", halign="center"))

# Generate the text geometry
#text_geom = text_3d(text_string, font_size, text_height)
text_geom = multi_line_text(text_string.split("\n"), line_spacing, font_size, text_height)

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

#text_mesh.show()


existing_mesh = "../stls/pencil_case_travel_tube/body.stl"
existing_mesh = trimesh.load_mesh(existing_mesh)

# Assuming mesh2 is a cylinder
bounding_box = existing_mesh.bounding_box_oriented
# Extract the extents of the bounding box
extents = bounding_box.primitive.extents
# The radius would be half of the diameter, which is one of the extents
print(extents)
radius = extents[0] / 2  # Assuming x-axis holds the diameter


curved_mesh1 = curve_mesh_onto_cylinder(text_mesh, radius)

rotation_matrix = trimesh.transformations.rotation_matrix(
    angle=np.pi / 2,         # 90 degrees in radians
    direction=[0, 1, 0],     # Rotation around the y-axis
    point=[0, 0, 0]          # Optional: rotation around the origin
)

# Apply the rotation to the mesh
curved_mesh1.apply_transform(rotation_matrix)
# curved_mesh1.show()
curved_mesh1.apply_translation([0, 0, -extents[2]/2])

existing_mesh = existing_mesh.union(curved_mesh1)
# existing_mesh.show()

# Path for the output STL file
stl_path = os.path.join(output_dir, 'pencil_box_with_text.stl')

# Export to STL
existing_mesh.export(stl_path)