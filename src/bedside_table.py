import trimesh
import numpy as np
from threaded_cylinder import create_threaded_cylinder
from shapely.geometry import Polygon


hole_width = 31.75 ## in mm
hole_length = 69.85 / 2 # in mm
support_thickness = 10 ## in mm
hole_length -= support_thickness / 2
support_short = 30 ## in mm
support_long = 90 ## in mm
extra_support_length = 30 ## in mm

pan_size = 170 ## in mm
pan_thickness = 5 ## in mm
pan_wallheight = 3 ## in mm
pan_wallthickness = 2 ## in mm

bolt_radius = 2
nut_radius = 5
nut_thickness1 = 4
nut_thickness2 = 2
thread_thickness = 1.5  # Thickness of the thread
thread_pitch = 2      # Distance between thread peaks
cutout_adj = 0.5

def build_support_shape():
    box1 = trimesh.creation.box([support_short, support_thickness, support_thickness])
    box1 = box1.apply_translation([support_short / 2 * (-1), support_thickness / 2 * (-1),support_thickness / 2])

    box2 = trimesh.creation.box([support_thickness, hole_length+support_thickness, support_thickness])
    box2 = box2.apply_translation([support_thickness/2, (hole_length+support_thickness) / 2 * (-1), support_thickness/2])

    box3 = trimesh.creation.box([hole_width, support_thickness, support_thickness])
    box3 = box3.apply_translation([hole_width/2+support_thickness, support_thickness/2*(-1) - hole_length, support_thickness/2])

    box4 = trimesh.creation.box([support_thickness, hole_length+support_thickness+extra_support_length, support_thickness])
    box4 = box4.apply_translation([support_thickness/2 + support_thickness + hole_width, (hole_length+support_thickness) / 2 * (-1)-extra_support_length/2, support_thickness/2])

    box5 = trimesh.creation.box([support_long, support_thickness, support_thickness])
    box5 = box5.apply_translation([support_long/2 + 2 * support_thickness + hole_width, support_thickness/2*(-1), support_thickness/2])

    box6 = trimesh.creation.box([support_thickness, hole_length+support_thickness+extra_support_length, support_thickness])
    box6 = box6.apply_translation([support_thickness/2 + support_thickness + hole_width + support_long, (hole_length+support_thickness) / 2 * (-1)-extra_support_length/2, support_thickness/2])


    support = trimesh.boolean.union([box1, box2, box3, box4, box5, box6 ])
    return support

def yz_mirror(mesh):
    # Create a transformation matrix for mirroring along the y-z plane (flipping x-axis)
    mirror_matrix = np.array([
        [ 1,  0,  0,  0],
        [ 0, -1,  0,  0],
        [ 0,  0,  1,  0],
        [ 0,  0,  0,  1]
    ])

    # Apply the transformation
    mesh = mesh.apply_transform(mirror_matrix)    
    return mesh

def build_pan():
    pan_base = trimesh.creation.box([pan_size, pan_size, pan_thickness])
    
    pan_wall1 = trimesh.creation.box([pan_size - 2 * pan_wallthickness, pan_wallthickness, pan_wallheight])
    pan_wall1 = pan_wall1.apply_translation([0, (pan_size - pan_wallthickness) / 2 * (-1), pan_wallheight/2 + pan_thickness/2])

    pan_wall2 = trimesh.creation.box([pan_size - 2 * pan_wallthickness, pan_wallthickness, pan_wallheight])
    pan_wall2 = pan_wall2.apply_translation([0, (pan_size - pan_wallthickness) / 2, pan_wallheight/2 + pan_thickness/2])

    pan_wall3 = trimesh.creation.box([pan_wallthickness, pan_size, pan_wallheight])
    pan_wall3 = pan_wall3.apply_translation([(pan_size - pan_wallthickness) / 2 * (-1), 0, pan_wallheight/2 + pan_thickness/2])

    pan_wall4 = trimesh.creation.box([pan_wallthickness, pan_size, pan_wallheight])
    pan_wall4 = pan_wall4.apply_translation([(pan_size - pan_wallthickness) / 2, 0, pan_wallheight/2 + pan_thickness/2])


    pan = trimesh.boolean.union([pan_base, pan_wall1, pan_wall2, pan_wall3, pan_wall4])
    pan = pan.apply_translation([support_thickness + pan_size / 2 + hole_width,0,pan_thickness/2+support_thickness])
    return pan


def create_hexgon_prism(radius=1.0, height=2.0):
    # Define the number of sides for the hexagon (6 for a hexagon)
    num_sides = 6

    # Generate points for the hexagon base
    angles = np.linspace(0, 2 * np.pi, num_sides, endpoint=False)
    hexagon_points = np.column_stack((np.cos(angles) * radius, np.sin(angles) * radius))

    # Create a shapely polygon for the hexagon base
    hexagon = Polygon(hexagon_points)

    # Use trimesh to extrude the polygon into a prism
    hexagon_prism = trimesh.creation.extrude_polygon(hexagon, height)    
    return hexagon_prism

def create_bolt(height, cap_thickness, cutout_adj=0):
    thread = create_threaded_cylinder(bolt_radius+cutout_adj, height, thread_thickness, thread_pitch)
    cap = create_hexgon_prism(nut_radius, cap_thickness)
    cap = cap.apply_translation([0, 0, cap_thickness*(-1.0)])
    mesh = trimesh.boolean.union([thread, cap])
    # mesh = mesh.apply_translation([0, 0, cap_thickness])
    return mesh

def rotate_90_around_x(mesh):
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(270),  # Angle in radians
        [1, 0, 0]        # Rotation axis (x-axis)
    )

    # Apply the rotation
    mesh.apply_transform(rotation_matrix)    
    return mesh

def rotate_180_around_x(mesh):
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(180),  # Angle in radians
        [1, 0, 0]        # Rotation axis (x-axis)
    )

    # Apply the rotation
    mesh.apply_transform(rotation_matrix)    
    return mesh

bolt1 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness1)
bolt1_cutout = create_bolt(support_thickness*2+nut_thickness1, nut_thickness1, cutout_adj)
bolt1_cutout2 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness1, cutout_adj)


bolt2 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness2)
bolt2_cutout = create_bolt(support_thickness*2+nut_thickness1, nut_thickness2, cutout_adj)
bolt2_cutout2 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness2, cutout_adj)
bolt2_cutout3 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness2, cutout_adj)
bolt2_cutout4 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness2, cutout_adj)
bolt2_cutout5 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness2, cutout_adj)
bolt2_cutout6 = create_bolt(support_thickness*2+nut_thickness1, nut_thickness2, cutout_adj)


hexagon_prism= create_hexgon_prism(nut_radius, nut_thickness1)

support = build_support_shape()
support_mirror = yz_mirror(build_support_shape())

pan = build_pan()

## position bolt1_cutout and bolt2_cutout
hexagon_prism = hexagon_prism.apply_translation([0, 0, nut_thickness1/2+nut_thickness1])
nut = hexagon_prism.difference(bolt1_cutout)
nut.export("~/Downloads/bedside_table_nut.stl")

bolt1.export("~/Downloads/bedside_table_bolt1.stl")

bolt2.export("~/Downloads/bedside_table_bolt2.stl")


bolt1_cutout = rotate_90_around_x(bolt1_cutout)
bolt1_cutout = bolt1_cutout.apply_translation([-support_short/2, -support_thickness, support_thickness/2.0])
bolt1_cutout2 = rotate_90_around_x(bolt1_cutout2)
bolt1_cutout2 = bolt1_cutout2.apply_translation([support_thickness*2 + hole_width + support_long *3/4, -support_thickness, support_thickness/2.0])

bolt2_cutout = rotate_180_around_x(bolt2_cutout)
bolt2_cutout = bolt2_cutout.apply_translation([support_thickness*2 + hole_width + support_long /2, support_thickness/2, nut_thickness2 + pan_thickness + support_thickness])
bolt2_cutout2 = rotate_180_around_x(bolt2_cutout2)
bolt2_cutout2 = bolt2_cutout2.apply_translation([support_thickness*2 + hole_width + support_long /4, -support_thickness/2, nut_thickness2 + pan_thickness + support_thickness])

bolt2_cutout3 = rotate_180_around_x(bolt2_cutout3)
bolt2_cutout3 = bolt2_cutout3.apply_translation([support_thickness*1.5 + hole_width + pan_wallthickness*0.2, -support_thickness/2-extra_support_length*2/3 - hole_length, nut_thickness2 + pan_thickness + support_thickness])

bolt2_cutout4 = rotate_180_around_x(bolt2_cutout4)
bolt2_cutout4 = bolt2_cutout4.apply_translation([support_thickness*1.5 + hole_width + pan_wallthickness*0.2, support_thickness/2+extra_support_length*2/3 + hole_length, nut_thickness2 + pan_thickness + support_thickness])

bolt2_cutout5 = rotate_180_around_x(bolt2_cutout5)
bolt2_cutout5 = bolt2_cutout5.apply_translation([support_thickness/2 + support_thickness + hole_width + support_long, -support_thickness/2-extra_support_length*2/3 - hole_length, nut_thickness2 + pan_thickness + support_thickness])

bolt2_cutout6 = rotate_180_around_x(bolt2_cutout6)
bolt2_cutout6 = bolt2_cutout6.apply_translation([support_thickness/2 + support_thickness + hole_width + support_long, support_thickness/2+extra_support_length*2/3 + hole_length, nut_thickness2 + pan_thickness + support_thickness])



# support2 = trimesh.boolean.union([support, support_mirror, pan, bolt1_cutout, bolt1_cutout2, bolt2_cutout, bolt2_cutout2, bolt2_cutout3, bolt2_cutout4, bolt2_cutout5, bolt2_cutout6])
# support2.show()

support = support.difference(bolt1_cutout)
support = support.difference(bolt1_cutout2)
support = support.difference(bolt2_cutout2)
support = support.difference(bolt2_cutout3)
support = support.difference(bolt2_cutout5)


support_mirror = support_mirror.difference(bolt1_cutout)
support_mirror = support_mirror.difference(bolt1_cutout2)
support_mirror = support_mirror.difference(bolt2_cutout)
support_mirror = support_mirror.difference(bolt2_cutout4)
support_mirror = support_mirror.difference(bolt2_cutout6)

pan = pan.difference(bolt2_cutout)
pan = pan.difference(bolt2_cutout2)
pan = pan.difference(bolt2_cutout3)
pan = pan.difference(bolt2_cutout4)
pan = pan.difference(bolt2_cutout5)
pan = pan.difference(bolt2_cutout6)

support.export("~/Downloads/bedside_table_support.stl")
support_mirror.export("~/Downloads/bedside_table_support_mirror.stl")
pan.export("~/Downloads/bedside_table_pan.stl")


# support_assemble = trimesh.boolean.union([support, support_mirror, pan])
# support_assemble.show()

