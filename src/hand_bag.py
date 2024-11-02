import trimesh
import numpy as np
from trimesh.creation import extrude_polygon
from shapely.geometry import box
from shapely.affinity import scale
from shapely.ops import unary_union
import trimesh.transformations as tra


def create_rounded_rectangle(length, width, radius, height=1.0):
    # Step 1: Create the center box
    center_box = trimesh.primitives.Box(extents=[length - 2 * radius, width - 2 * radius, height])
    center_box.apply_translation([0, 0, height / 2])

    # Step 2: Create the four corner cylinders
    corners = []
    corner_positions = [
        (length / 2 - radius, width / 2 - radius),   # Top right
        (-length / 2 + radius, width / 2 - radius),  # Top left
        (length / 2 - radius, -width / 2 + radius),  # Bottom right
        (-length / 2 + radius, -width / 2 + radius)  # Bottom left
    ]
    for pos in corner_positions:
        cylinder = trimesh.primitives.Cylinder(radius=radius, height=height, sections=32)
        cylinder.apply_translation([pos[0], pos[1], height / 2])
        corners.append(cylinder)
    
    # Step 3: Create the two horizontal boxes
    horizontal_boxes = []
    horizontal_box_top = trimesh.primitives.Box(extents=[length - 2*radius, 2 * radius, height])
    horizontal_box_top.apply_translation([0, width / 2 - radius, height / 2])
    horizontal_boxes.append(horizontal_box_top)
    
    horizontal_box_bottom = trimesh.primitives.Box(extents=[length - 2*radius, 2 * radius, height])
    horizontal_box_bottom.apply_translation([0, -width / 2 + radius, height / 2])
    horizontal_boxes.append(horizontal_box_bottom)
    
    # Step 4: Create the two vertical boxes
    vertical_boxes = []
    vertical_box_right = trimesh.primitives.Box(extents=[2 * radius, width - 2*radius, height])
    vertical_box_right.apply_translation([length / 2 - radius, 0, height / 2])
    vertical_boxes.append(vertical_box_right)
    
    vertical_box_left = trimesh.primitives.Box(extents=[2 * radius, width - 2*radius, height])
    vertical_box_left.apply_translation([-length / 2 + radius, 0, height / 2])
    vertical_boxes.append(vertical_box_left)
    
    # Step 5: Combine all parts (center box, corners, horizontal and vertical boxes)
    combined = center_box
    for part in corners + horizontal_boxes + vertical_boxes:
    # for part in corners:
        combined = combined.union(part)

    return combined

def create_thin_rounded_rectangle_ring(length, width, radius, thickness, height=1.0):
    # Step 1: Create the outer rounded rectangle
    rectangle1 = create_rounded_rectangle(length, width, radius, height)
    
    # Step 2: Create the inner rounded rectangle (smaller dimensions)
    rectangle2 = create_rounded_rectangle(
        length - thickness, 
        width - thickness, 
        radius - thickness / 2, 
        height
    )
    
    # Step 3: Subtract the inner rectangle from the outer rectangle to create the ring
    ring = rectangle1.difference(rectangle2)
    
    return ring

def create_a_bag(base_length, base_width, corner_radius, base_thickness, wall_thickness, bag_height, taper_rate=1.0):
    steps = int(bag_height / wall_thickness)
    taper_step = (taper_rate - 1.0) / steps
    if abs(taper_step * base_length) > 0.5 * wall_thickness:
        taper_step = np.sign(taper_step) * 0.5 * wall_thickness / base_length
    base = create_rounded_rectangle(base_length, base_width, corner_radius, base_thickness)
    for ii in range(steps):
        wall = create_thin_rounded_rectangle_ring(base_length * (1.0 + ii * taper_step), base_width * (1.0 + ii * taper_step), corner_radius * (1.0 + ii * taper_step), wall_thickness, wall_thickness)
        wall.apply_translation([0, 0, base_thickness / 2+ii*wall_thickness + wall_thickness/2])
        base = base.union(wall)
    return base


def create_a_bag_smooth(base_length, base_width, corner_radius, base_thickness, wall_thickness, bag_height, l_taper_rate=1.0, w_taper_rate=1.0):
    steps = int(bag_height / wall_thickness)
    l_taper_step = (l_taper_rate - 1.0) / steps
    w_taper_step = (w_taper_rate - 1.0) / steps
    if abs(l_taper_step * base_length) > 0.5 * wall_thickness:
        l_taper_step = np.sign(l_taper_step) * 0.5 * wall_thickness / base_length
    if abs(w_taper_step * base_width) > 0.5 * wall_thickness:
        w_taper_step = np.sign(w_taper_step) * 0.5 * wall_thickness / base_width
    c_taper_step = l_taper_step * 0.5 + w_taper_step * 0.5
    base = create_rounded_rectangle(base_length, base_width, corner_radius, base_thickness)
    interior = None
    for ii in range(steps):
        wall = create_rounded_rectangle(base_length * (1.0 + ii * l_taper_step), base_width * (1.0 + ii * w_taper_step), corner_radius * (1.0 + ii * c_taper_step), wall_thickness)
        wall.apply_translation([0, 0, base_thickness / 2+ii*wall_thickness + wall_thickness/2])
        base = base.union(wall)
        wall = create_rounded_rectangle(base_length * (1.0 + ii * l_taper_step)-wall_thickness, base_width * (1.0 + ii * w_taper_step) - wall_thickness, corner_radius * (1.0 + ii * c_taper_step), wall_thickness)
        wall.apply_translation([0, 0, base_thickness / 2+ii*wall_thickness + wall_thickness/2])
        if interior is None:
            interior = wall
        else :
            interior = interior.union(wall)
    base = base.convex_hull
    interior = interior.convex_hull
    base = base.difference(interior)
    return base


def create_a_bag_with_handle_holes(bag, base_width, base_thickness, bag_height, hole_radius, hole_distance):
    # Step 2: Calculate the height of the holes (top of the bag minus 10x base_thickness)
    hole_height = bag_height - 3 * base_thickness

    # Step 3: Position the holes on the long side of the bag
    # We place two cylinders symmetrically on both long sides
    hole_positions = [
        (-(hole_distance / 2), 0),  # Left hole on the long side
        (hole_distance / 2, 0)      # Right hole on the long side
    ]

    # Step 4: Create two long cylinders for the holes
    holes = []
    for pos in hole_positions:
        hole = trimesh.primitives.Cylinder(radius=hole_radius, height=base_width * 2)
        # Step 5: Rotate the cylinder to align it with the long side
        rotation_matrix = tra.rotation_matrix(np.pi / 2, [1, 0, 0])
        hole.apply_transform(rotation_matrix)
        
        # Step 6: Translate the cylinder to the correct position
        hole.apply_translation([pos[0], 0, hole_height])

        holes.append(hole)

    # Step 5: Subtract the holes from the bag
    for hole in holes:
        bag = bag.difference(hole)

    return bag


def create_handle(hole_radius, base_thickness, handle_distance, tapered_base_width):
    # Step 1: Create the main handle (Box 1)
    length_1 = np.pi * handle_distance / 2 + base_thickness * 3 * 2 + tapered_base_width * 2 * 2**0.5
    width_1 = hole_radius * 2
    height_1 = base_thickness
    handle_main = trimesh.primitives.Box(extents=[length_1, width_1, height_1])
    
    # Step 2: Create the two side boxes (Box 2)
    length_2 = base_thickness * 2
    width_2 = hole_radius * 6
    height_2 = base_thickness
    
    side_box_left = trimesh.primitives.Box(extents=[length_2, width_2, height_2])
    side_box_left.apply_translation([-(length_1 / 2), 0, 0])  # Move to the left end of Box 1
    
    side_box_right = trimesh.primitives.Box(extents=[length_2, width_2, height_2])
    side_box_right.apply_translation([(length_1 / 2), 0, 0])  # Move to the right end of Box 1
    
    # Step 3: Union the main handle (Box 1) with the two side boxes (Box 2)
    handle = handle_main.union([side_box_left, side_box_right])
    
    return handle

def add_divider(bag, base_width, base_thickness, bag_height, divider_height, wall_thickness, w_taper_rate, divider_position=0):
    steps = int(bag_height / wall_thickness)
    iter_steps = int(divider_height / wall_thickness)
    w_taper_step = (w_taper_rate - 1.0) / steps
    if abs(w_taper_step * base_width) > 0.5 * wall_thickness:
        w_taper_step = np.sign(w_taper_step) * 0.5 * wall_thickness / base_width
    base = trimesh.primitives.Box(extents=[wall_thickness, base_width* (1.0 + w_taper_step), wall_thickness])
    base.apply_translation([divider_position, 0, base_thickness/2+wall_thickness/2])
    for ii in range(1, iter_steps):
        layer = trimesh.primitives.Box(extents=[wall_thickness, base_width*(1.0+w_taper_step * (ii+1)), wall_thickness])
        layer.apply_translation([divider_position, 0, base_thickness/2+wall_thickness/2+ii*wall_thickness])
        base = base.union(layer)
    divider = base.convex_hull
    bag = bag.union(divider)
    return bag


def create_rainbow_shape_handle(hole_radius, base_thickness, handle_distance, tapered_base_width):
    # Step 1: Create the rainbow (half circle) shape
    outer_radius = handle_distance / 2
    inner_radius = (handle_distance / 2) - hole_radius * 2
    
    # Create the outer circle and inner circle (subtracted to create a ring)
    outer_cylinder = trimesh.primitives.Cylinder(radius=outer_radius, height=base_thickness, sections=64)
    inner_cylinder = trimesh.primitives.Cylinder(radius=inner_radius, height=base_thickness, sections=64)
    
    # Subtract inner cylinder from outer cylinder to create the ring (rainbow shape)
    rainbow = outer_cylinder.difference(inner_cylinder)

    # Apply rotation and translation to position the rainbow in the positive Y side of the XY plane
    # rotation_matrix = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])  # Rotate to lie on XY plane
    # rainbow.apply_transform(rotation_matrix)
    # rainbow.show()    

    # Step 3: Cut the outer and inner cylinders in half (to get a half-rainbow)
    # Create a cutting plane to remove the negative Y half
    cutting_plane = trimesh.creation.box(extents=[outer_radius * 2, outer_radius*2, base_thickness], transform=trimesh.transformations.translation_matrix([0, -outer_radius, 0]))

    
    # Step 4: Subtract the inner half from the outer half to get the rainbow
    rainbow = rainbow.difference(cutting_plane)

    # Step 2: Create two boxes at the bottom of the rainbow (connected to the base)
    length_1 = hole_radius * 2
    width_1 = base_thickness * 3 + tapered_base_width * 2**0.5
    height_1 = base_thickness

    box_left = trimesh.primitives.Box(extents=[length_1, width_1, height_1])
    box_left.apply_translation([(handle_distance / 2) - hole_radius, -width_1 / 2, 0])  # Left side box

    box_right = trimesh.primitives.Box(extents=[length_1, width_1, height_1])
    box_right.apply_translation([-(handle_distance / 2) + hole_radius, -width_1 / 2, 0])  # Right side box
    
    # Step 3: Create the side boxes
    width_2 = base_thickness * 2
    length_2 = hole_radius * 6
    height_2 = base_thickness

    side_box_left = trimesh.primitives.Box(extents=[length_2, width_2, height_2])
    side_box_left.apply_translation([(handle_distance / 2) - hole_radius, -(width_1 + base_thickness), 0])

    side_box_right = trimesh.primitives.Box(extents=[length_2, width_2, height_2])
    side_box_right.apply_translation([-(handle_distance / 2) + hole_radius, -(width_1 + base_thickness), 0])

    # Step 4: Combine (union) all the parts together
    handle = rainbow.union([box_left, box_right, side_box_left, side_box_right])

    return handle

if __name__ == "__main__":

    # Test the function
    length = 180  # mm
    width = 100    # mm
    corner_radius = 10  # mm
    base_thickness = 5  # mm
    wall_thickness = 2.5
    bag_height = 150
    hole_radius = 5
    hole_distance = 70
    divider_height = bag_height * 0.7
    #l_taper_rate = 1.0
    #w_taper_rate = 0.7
    l_taper_rate = 1.2
    w_taper_rate = 1.2
    #base_3d = create_rounded_rectangle(length, width, corner_radius, height=base_thickness)
    # bag = create_a_bag_with_handle_holes(length, width, corner_radius, base_thickness, wall_thickness, bag_height, hole_radius, hole_distance, taper_rate=1.1)

    bag = create_a_bag_smooth(length, width, corner_radius, base_thickness, wall_thickness, bag_height,  l_taper_rate=l_taper_rate, w_taper_rate=w_taper_rate)
    bag = create_a_bag_with_handle_holes(bag, width, base_thickness, bag_height, hole_radius, hole_distance)
    # bag = add_divider(bag, width, base_thickness, bag_height, divider_height, wall_thickness, w_taper_rate, divider_position = 0)

    # bag.show()
    handle = create_rainbow_shape_handle(hole_radius, base_thickness, hole_distance, width * w_taper_rate)
    # handle.show()

    # Step 6: Export as STL
    bag.export('~/Downloads/handbag_body.stl')
    handle.export('~/Downloads/handle_strips.stl')

    print("STL files 'handbag_body.stl' and 'handle_strips.stl' have been exported successfully.")

