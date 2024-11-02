import trimesh
import numpy as np

def create_menger_sponge(level, size, position=(0, 0, 0)):
    if level == 0:
        # Base case: create a simple cube
        cube = trimesh.creation.box(extents=[size, size, size])
        cube.apply_translation(position)
        return cube

    # Subdivide the cube into 27 smaller cubes and remove the middle ones
    new_size = size / 3.0
    cubes = []
    offsets = [-new_size, 0, new_size]
    for x in offsets:
        for y in offsets:
            for z in offsets:
                if abs(x) + abs(y) + abs(z) > new_size:
                    new_position = (position[0] + x, position[1] + y, position[2] + z)
                    cubes.append(create_menger_sponge(level - 1, new_size, new_position))
    
    # Combine all smaller cubes into one mesh
    return trimesh.util.concatenate(cubes)

# Parameters for the Menger sponge
level = 3  # Increase the level for more detail
size = 50

# Create the Menger sponge
menger_sponge = create_menger_sponge(level, size)

# Export to STL
menger_sponge.export('~/Downloads/menger_sponge.stl')
