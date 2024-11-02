import numpy as np
from PIL import Image
import trimesh
import os
import image_utils
from utils import validate_and_repair_mesh

# Function to create a block at a specific position
def create_block(x, y, height, pixel_size=1):
    box = trimesh.creation.box([pixel_size, pixel_size, height])
    box = box.apply_translation([x, y, 0])
    return box
    # # Define the vertices of a rectangular prism (cuboid) for each block
    # vertices = [
    #     [x, y, 0],         # Bottom face
    #     [x+pixel_size, y, 0],
    #     [x+pixel_size, y+pixel_size, 0],
    #     [x, y+pixel_size, 0],
    #     [x, y, height],    # Top face
    #     [x+pixel_size, y, height],
    #     [x+pixel_size, y+pixel_size, height],
    #     [x, y+pixel_size, height]
    # ]
    
    # # Define faces using the vertices
    # faces = [
    #     [0, 1, 2], [0, 2, 3], # Bottom face
    #     [4, 5, 6], [4, 6, 7], # Top face
    #     [0, 1, 5], [0, 5, 4], # Side faces
    #     [1, 2, 6], [1, 6, 5],
    #     [2, 3, 7], [2, 7, 6],
    #     [3, 0, 4], [3, 4, 7]
    # ]
    
    # return trimesh.Trimesh(vertices=vertices, faces=faces)

def center_mesh(mesh):
    # Get the bounding box
    bbox_min, bbox_max = mesh.bounds
    
    # Calculate the center of the bounding box
    center = (bbox_min + bbox_max) / 2
    
    # Translate the mesh by the negative center to move it to (0, 0, 0)
    mesh.apply_translation(-center)
    
    return mesh

def create_extruded_mesh(matrix, length, width, height):
    blocks = []
    rows, cols = matrix.shape
    
    for i in range(rows):
        for j in range(cols):
            if matrix[i, j] == 1:
                # Create a block at (i, j) with the specified height
                block = create_block(i * length/rows, j * width / cols, height, pixel_size=length/rows)
                # block.show()
                blocks.append(block)
    
    # Combine all blocks into a single mesh
    # combined = trimesh.util.concatenate(blocks)
    combined = trimesh.boolean.union(blocks)
    # combined = trimesh.union(blocks)
    if not combined.is_volume:
        combined = trimesh.util.concatenate(blocks)
    # combined = validate_and_repair_mesh(combined)

    return center_mesh(combined)

def create_enclosing_box(mesh, z_offset=None):
    # Get the bounding box of the original mesh
    bounding_box = mesh.bounding_box
    
    if z_offset is None:
        z_offset = bounding_box.extents[2]

    # Create a new box based on the bounding box size
    box_mesh = trimesh.creation.box(extents=list(bounding_box.extents[:2])+[z_offset])
    


    # Move the box down along the z-axis by z_offset
    box_mesh.apply_translation([0, 0, -z_offset])
    
    return box_mesh

# Combine the original mesh and the box
def combine_mesh_with_box(mesh, box_mesh):
    # Concatenate the original mesh with the box mesh
    combined_mesh = trimesh.util.concatenate([mesh, box_mesh])
    return combined_mesh

def scale_mesh(mesh, scale_factor):
    # Apply the scale factor to the mesh
    mesh.apply_scale(scale_factor)
    return mesh


def image_to_3d_model(image_path, grayscale_output_path=None, final_width=100, final_length=100, final_height=2, invert=True):
    # Load the image
    img_array = image_utils.image_to_zeroones(image_path, grayscale_output_path, invert)
    final_width = img_array.shape[0] *1.0 / img_array.shape[1] * final_length

    img_mesh = create_extruded_mesh(img_array, final_width, final_length, final_height)
    # img_mesh.show()
    return img_mesh

def image_to_3d_model_with_board(image_path, output_path, grayscale_output_path=None, final_width=100, final_length=100, final_height=2, invert=True):
    img_mesh = image_to_3d_model(image_path, grayscale_output_path, final_width, final_length, final_height, invert)
    bottom_box = create_enclosing_box(img_mesh)
    # bottom_box.show()

    mesh = combine_mesh_with_box(img_mesh, bottom_box)
    # mesh = img_mesh   
    print(mesh.is_volume)
    # Export the mesh to an STL file
    mesh.export(output_path)
    return mesh

if __name__ == "__main__":
    # Example usage
    # image_path = os.path.expanduser("~/Downloads/WechatIMG21.jpg")  # Replace with your image path
    # image_path = os.path.expanduser("~/Downloads/constellations.png")
    # output_path = os.path.expanduser("~/Downloads/3d_model_with_board2.stl")  # Replace with your desired output path
    # grayscale_output_path = os.path.expanduser("~/Downloads/grayscale_image.jpg")  # Path to save the grayscale image
    ## good for photo
    # image_to_3d_model_with_board(image_path, output_path, grayscale_output_path=grayscale_output_path, final_width=150, final_length=150, final_height=2, board_thickness=0.5)  # Adjust as needed
    # image_to_3d_model_with_board(image_path, output_path, grayscale_output_path=grayscale_output_path, final_width=100, final_length=100, final_height=2, invert=False)  # Adjust as needed
    #image_to_3d_model_with_board(image_path, output_path, grayscale_output_path=grayscale_output_path, final_width=100, final_length=100, final_height=2)  # Adjust as needed
    # image_to_3d_model_with_board(image_path, output_path, grayscale_output_path=grayscale_output_path, final_width=150, final_length=150, final_height=10, board_thickness=1)  # Adjust as needed

    image_path = os.path.expanduser("~/Downloads/ursamajor.jpg")
    img_array = image_utils.image_to_zeroones(image_path, None, False)
    for ii in range(2):
        img_array = image_utils.make_ones_bigger(img_array)
    img_array = image_utils.zeroones_to_connected(img_array, path_width=20, do_plot=True)
    final_width = img_array.shape[0] *1.0 / img_array.shape[1] * 100
    img_mesh = create_extruded_mesh(img_array, final_width, 100, 2)
    img_mesh.show()