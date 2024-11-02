import trimesh
import numpy as np

def create_string_tie(a, b):
    # Step 1: Create the first box with dimensions a x b x b, centered at (0, 0, 0)
    box_1 = trimesh.primitives.Box(extents=[a, b, b])
    
    # Step 2: Create the second box with dimensions b x 3b x b, centered at (a/2 + b/2, 0, 0)
    box_2 = trimesh.primitives.Box(extents=[b, 5 * b, b])
    box_2.apply_translation([a / 2 + b / 2, 0, 0])  # Move it to the correct position
    
    # Step 3: Create the ring (donut shape) with inner_radius=b/2 and outer_radius=b
    outer_cylinder = trimesh.primitives.Cylinder(radius=b * 1.5, height=b, sections=64)
    inner_cylinder = trimesh.primitives.Cylinder(radius=b, height=b, sections=64)
    
    # Subtract the inner cylinder from the outer cylinder to create the ring
    ring = outer_cylinder.difference(inner_cylinder)
    ring.apply_translation([-a / 2 - b / 2, 0, 0])  # Position the ring correctly
    
    # Step 4: Union the three shapes together
    string_tie = box_1.union([box_2, ring])
    
    return string_tie

length = 50
width = 1
# Example usage of the function
string_tie_mesh = create_string_tie(a=length, b=width)

# Visualize the result
# string_tie_mesh.show()
string_tie_mesh.export('~/Downloads/string_tie.stl')