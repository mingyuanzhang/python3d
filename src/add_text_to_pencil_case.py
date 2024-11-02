import trimesh
from trimesh.creation import box
from solid import text, linear_extrude, scad_render
import os
import subprocess
import numpy as np
from solid.utils import translate


def curve_mesh_onto_cylinder(mesh, radius):
    
    for vertex in mesh.vertices:
        # Get the original x, y, z coordinates
        x, y, z = vertex

        # Convert x (linear distance) to an angular displacement around the cylinder
        angle = x / radius

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
text_string = "Name"
font_size = 10  # Font size
line_spacing = font_size+3
text_height = 2  # Height of the text
sign_borders = 10
board_thickness = 2

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
    direction=[1, 0, 0],     # Rotation around the y-axis
    point=[0, 0, 0]          # Optional: rotation around the origin
)

# Apply the rotation to the mesh
curved_mesh1.apply_transform(rotation_matrix)
# curved_mesh1.show()
curved_mesh1.apply_translation([0, 0, -extents[2]/4])

existing_mesh = existing_mesh.union(curved_mesh1)
existing_mesh.show()

# Path for the output STL file
stl_path = os.path.join(output_dir, 'pencil_box_with_name.stl')

# Export to STL
existing_mesh.export(stl_path)