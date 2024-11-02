import trimesh
import numpy as np
import utils

# Function to create a chain link as per your description
def create_custom_chain_link(
    major_radius=1.0,
    minor_radius=0.3,
    elongation=0.2,
    tube_sections=32,
    cylinder_sections=32
):
    """
    Creates a chain link by cutting a torus in half, separating the halves,
    and connecting them with two cylinders.

    Parameters:
    - major_radius: Major radius of the torus.
    - minor_radius: Minor radius (tube radius) of the torus.
    - elongation: The amount by which to separate the two halves.
    - sections: Number of sections around the main ring of the torus.
    - tube_sections: Number of sections around the tube of the torus.
    - cylinder_sections: Number of sections around the connecting cylinders.
    """
    # Create the torus
    torus = trimesh.creation.torus(
        major_radius=major_radius,
        minor_radius=minor_radius,
        tube_sections=tube_sections
    )

    # Slice the torus along the plane
    # This modifies the torus mesh to include the slicing plane
    half2 = utils.slice_plane_x(torus, 0, "right")
    half1 = utils.slice_plane_x(torus, 0, "left")

    # Move the halves apart along the X-axis
    half1.apply_translation([-elongation / 2, 0, 0])
    half2.apply_translation([elongation / 2, 0, 0])

    # Create the connecting cylinders
    # Positions for cylinders at Y = ±(major_radius), Z = 0
    cylinder_radius = minor_radius  # Same as the torus tube radius
    cylinder_length = elongation    # Length to span the gap between halves

    # Function to create a cylinder between two points
    def create_cylinder_between_points(start_point, end_point):
        # Calculate the vector between points
        vec = np.array(end_point) - np.array(start_point)
        # Cylinder height is the distance between points
        height = np.linalg.norm(vec)

        # Create cylinder along Z-axis
        cylinder = trimesh.creation.cylinder(
            radius=cylinder_radius,
            height=height,
            sections=cylinder_sections
        )
        # Calculate rotation matrix to align cylinder with vector
        direction = vec / height  # Normalize the vector
        # Find rotation axis and angle
        z_axis = np.array([0, 0, 1])
        rotation_axis = np.cross(z_axis, direction)
        if np.linalg.norm(rotation_axis) == 0:
            rotation_axis = [1, 0, 0]
            angle = 0
        else:
            angle = np.arccos(np.dot(z_axis, direction))
        # Create rotation matrix
        rotation = trimesh.transformations.rotation_matrix(
            angle, rotation_axis, point=[0, 0, 0]
        )
        # Apply rotation
        cylinder.apply_transform(rotation)
        # Move cylinder to start point
        cylinder.apply_translation((np.array(end_point) + np.array(start_point))/2)
        return cylinder

    # Define start and end points for the cylinders
    start_point1 = [-elongation / 2, major_radius, 0]
    end_point1 = [elongation / 2, major_radius, 0]

    start_point2 = [-elongation / 2, -major_radius, 0]
    end_point2 = [elongation / 2, -major_radius, 0]

    # Create the connecting cylinders
    cylinder1 = create_cylinder_between_points(start_point1, end_point1)
    cylinder2 = create_cylinder_between_points(start_point2, end_point2)

    # Combine the halves and cylinders into one mesh
    link = trimesh.util.concatenate([half1, half2, cylinder1, cylinder2])
    return link


def chain_from_links(link, num_links, link_elongation, link_shift):
    # Calculate the length of the link along the Z-axis
    # Since the torus lies primarily in the XY-plane, we'll consider the dimensions accordingly
    link_bounds = link.bounds
    link_size = link_bounds[1] - link_bounds[0]
    link_length_z = link_size[2]  # Length along Z-axis

    # List to hold the chain links
    links = []

    for i in range(num_links):
        # Copy the link to create a new instance
        new_link = link.copy()

        # Rotate every other link by 90 degrees around the X-axis to interlock them
        if i % 2 == 1:
            rotation = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
            new_link.apply_transform(rotation)
            # new_link.show()

        # Translate the link along the Z-axis
        translation_distance = i * (link_elongation + link_shift)
        # translation = trimesh.transformations.translation_matrix([0, 0, translation_distance])
        new_link = new_link.apply_translation([translation_distance, 0, 0])

        # Add the transformed link to the list
        links.append(new_link)

    # Combine all links into a single mesh
    chain = trimesh.util.concatenate(links)

    return chain


if __name__ == "__main__":

    # Parameters for the chain link
    base_radius = 5 ## in mm
    major_radius = 1.0 * base_radius   # Major radius of the torus
    minor_radius = 0.5 * base_radius   # Minor radius (thickness of the link)
    elongation = 3 * base_radius     # Gap between the two halves
    tube_sections = 32    # Smoothness of the torus tube
    cylinder_sections = 32  # Smoothness of the cylinders

    # Create the initial chain link
    link = create_custom_chain_link(
        major_radius=major_radius,
        minor_radius=minor_radius,
        elongation=elongation,
        tube_sections=tube_sections,
        cylinder_sections=cylinder_sections
    )

    # Now, assemble multiple links into a chain
    num_links = 10     # Number of links in the chain
    link_shift = (major_radius) / 2

    chain = chain_from_links(link, num_links, elongation, link_shift)
    # Visualize the chain
    # chain.show()
    chain.export("~/Downloads/chain.stl")

