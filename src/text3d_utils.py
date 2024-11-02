import trimesh
from trimesh.creation import box
from solid import text, linear_extrude, scad_render
import os
import subprocess


def text_3d_mesh(text_geom, text_height):
    # Render the text geometry to an OpenSCAD string
    scad_code = scad_render(text_geom)

    # Path for the OpenSCAD file
    scad_path = os.path.join("/tmp/", 'text.scad')

    # Write the OpenSCAD string to a file
    with open(scad_path, 'w') as f:
        f.write(scad_code)

    # Convert the OpenSCAD file to STL using OpenSCAD command line
    stl_path_text = os.path.join("/tmp/", 'text.stl')
    subprocess.run(['openscad', '-o', stl_path_text, scad_path])

    # Load the text geometry from the generated STL file
    text_mesh = trimesh.load_mesh(stl_path_text)

    # Center the text on the board
    text_bounds = text_mesh.bounding_box.extents
    text_translation = [
        0,
        0,
        text_height / 2
    ]
    text_mesh.apply_translation(text_translation)
    return text_mesh


def text_3d(text_string, size, height):
    return linear_extrude(height=height)(text(text_string, size=size, valign="center", halign="center"))


def multi_line_text(text_lines, line_spacing=10, size=10, height=5):
    lines = []
    for i, line in enumerate(text_lines):
        # Position each line by translating it down based on the line number
        lines.append(translate([0, -i * line_spacing, 0])(text(line, size=size, halign="center", valign="center")))
    return linear_extrude(height=height)(lines)


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
