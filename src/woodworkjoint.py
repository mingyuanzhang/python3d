import trimesh
import numpy as np

def stable_joint(box_l, box_w, box_h, notch_base, notch_top, notch_height, stick_radius):
    box1 = trimesh.creation.box(box_l, box_w, box_h)
    box1 = box1.apply_translation([box_l/2*(-1), 0, box_h/2])

    box2 = trimesh.creation.box(box_l, box_w, box_h)
    box2 = box2.apply_translation([box_l/2, 0, box_h/2])



def create_trapezoid_prism(b, t, h, depth):
    # Half-widths for base and top to make the prism symmetric around the origin
    half_b = b / 2
    half_t = t / 2
    half_depth = depth / 2

    # Define the vertices of the trapezoidal prism
    vertices = np.array([
        # Bottom face (y = -h/2)
        [-half_b, -h/2, -half_depth],  # Bottom-left-front (0)
        [half_b, -h/2, -half_depth],   # Bottom-right-front (1)
        [half_b, -h/2, half_depth],    # Bottom-right-back (2)
        [-half_b, -h/2, half_depth],   # Bottom-left-back (3)

        # Top face (y = h/2)
        [-half_t, h/2, -half_depth],   # Top-left-front (4)
        [half_t, h/2, -half_depth],    # Top-right-front (5)
        [half_t, h/2, half_depth],     # Top-right-back (6)
        [-half_t, h/2, half_depth]     # Top-left-back (7)
    ])

    # Define the faces using the indices of the vertices
    faces = [
        # Bottom face
        [0, 1, 2], [0, 2, 3],
        # Top face
        [4, 5, 6], [4, 6, 7],
        # Front face
        [0, 1, 5], [0, 5, 4],
        # Back face
        [2, 3, 7], [2, 7, 6],
        # Left face
        [0, 3, 7], [0, 7, 4],
        # Right face
        [1, 2, 6], [1, 6, 5]
    ]

    # Create the mesh
    trapezoid_prism = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    trapezoid_prism = trapezoid_prism.convex_hull
    return trapezoid_prism


def stable_joint(box_l, box_w, box_h, notch_base, notch_top, notch_height, stick_radius, wiggle_room=0.5):
    box1 = trimesh.creation.box([box_l, box_w, box_h])
    box1 = box1.apply_translation([box_l/2*(-1), 0, box_h/2])

    box2 = trimesh.creation.box([box_l, box_w, box_h])
    box2 = box2.apply_translation([box_l/2, 0, box_h/2])

    notch = create_trapezoid_prism(notch_base, notch_top, notch_height, box_h)
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [0, 0, 1]        # Rotation axis (x-axis)
    )
    # Apply the rotation
    notch.apply_transform(rotation_matrix)    
    notch = notch.apply_translation([notch_height/2, 0, box_h/2])

    notch_cut = create_trapezoid_prism(notch_base+wiggle_room, notch_top+wiggle_room, notch_height+wiggle_room, box_h)
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [0, 0, 1]        # Rotation axis (x-axis)
    )
    # Apply the rotation
    notch_cut.apply_transform(rotation_matrix)    
    notch_cut = notch_cut.apply_translation([notch_height/2, 0, box_h/2])

    male = trimesh.boolean.union([box1, notch])
    # male.show()
    female = box2.difference(notch_cut)
    # female.show()

    stick = trimesh.creation.cylinder(radius=stick_radius, height=box_w, sections=64)
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [1, 0, 0]        # Rotation axis (x-axis)
    )
    # Apply the rotation
    stick.apply_transform(rotation_matrix)       
    stick = stick.apply_translation([notch_height/2,0,box_h/2])
    
    stick_cut = trimesh.creation.cylinder(radius=stick_radius + wiggle_room/4, height=box_w, sections=64)
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(90),  # Angle in radians
        [1, 0, 0]        # Rotation axis (x-axis)
    )
    # Apply the rotation
    stick_cut.apply_transform(rotation_matrix)       
    stick_cut = stick_cut.apply_translation([notch_height/2,0,box_h/2])

    male = male.difference(stick_cut)
    female = female.difference(stick_cut)

    # all = trimesh.boolean.union([male, female, stick])
    # all.show()
    return male, female, stick

if __name__ == "__main__":
    box_l = 30
    box_w = 20
    box_h = 20
    notch_base = 10
    notch_top = 6
    notch_height = 10
    stick_radius = 2

    male, female, stick = stable_joint(box_l, box_w, box_h, notch_base, notch_top, notch_height, stick_radius)
    male.export("~/Downloads/woodwork_joint_male.stl")
    female.export("~/Downloads/woodwork_joint_female.stl")
    stick.export("~/Downloads/woodwork_joint_stick.stl")