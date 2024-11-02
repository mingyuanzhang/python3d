import trimesh


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