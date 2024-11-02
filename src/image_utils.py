import numpy as np
from collections import deque
from PIL import Image

import cv2
import numpy as np
import matplotlib.pyplot as plt

import copy

def bresenham_line(x1, y1, x2, y2):
    # List to store the path of points
    points = []
    
    # Calculate the deltas
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    # Determine the step direction
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    
    # Initialize the error term
    if dx > dy:
        err = dx // 2
    else:
        err = -dy // 2

    # Initialize the current point
    x, y = x1, y1

    while True:
        # Add the current point to the path
        points.append((x, y))
        
        # Check if the end point has been reached
        if x == x2 and y == y2:
            break
        
        # Store the error term temporarily
        e2 = err
        
        # Adjust the x-coordinate and error if necessary
        if e2 > -dx:
            err -= dy
            x += sx
        
        # Adjust the y-coordinate and error if necessary
        if e2 < dy:
            err += dx
            y += sy
    
    return points

def connect_all_zeros(matrix, path_width):
    max_x, max_y = matrix.shape
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # BFS function to find all connected components of 0s
    def find_components():
        visited = set()
        components = []

        def bfs(x, y):
            component = []
            queue = deque([(x, y)])
            visited.add((x, y))
            component.append((x, y))
            
            while queue:
                cx, cy = queue.popleft()
                
                # Explore neighbors
                for dx, dy in directions:
                    nx, ny = cx + dx, cy + dy
                    
                    if 0 <= nx < max_x and 0 <= ny < max_y and (nx, ny) not in visited and matrix[nx][ny] == 0:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        component.append((nx, ny))
            
            return component
        
        # Find all components of 0s
        for i in range(max_x):
            for j in range(max_y):
                if matrix[i][j] == 0 and (i, j) not in visited:
                    components.append(bfs(i, j))
        components = sorted(components, key=lambda x: len(x))        
        return components
    
    def find_bordering_ones(component):
        bordering_ones = set()
        
        for (x, y) in component:
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < max_x and 0 <= ny < max_y and matrix[nx][ny] == 1:
                    bordering_ones.add((nx, ny))
        
        return bordering_ones

    # Find neighboring 1s that could connect two components
    def find_min_lattice_distance_optimized(c1, c2):
        # Sort both collections by x-coordinate first, then by y-coordinate
        c1_sorted = sorted(c1, key=lambda p: (p[0], p[1]))
        c2_sorted = sorted(c2, key=lambda p: (p[0], p[1]))

        # Initialize variables
        i, j = 0, 0
        min_distance = float('inf')
        best_pair = None

        # Two-pointer technique
        while i < len(c1_sorted) and j < len(c2_sorted):
            p1 = c1_sorted[i]
            p2 = c2_sorted[j]

            # Calculate Manhattan distance
            dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

            if dist < min_distance:
                min_distance = dist
                best_pair = (p1, p2)

            if min_distance == 0:
                break

            # Move the pointer that is behind (try to get closer points)
            if p1[0] < p2[0] or (p1[0] == p2[0] and p1[1] < p2[1]):
                i += 1
            else:
                j += 1

        return best_pair, min_distance
    
    components = find_components()

    for component in components:
        if len(component) <= 4: ## less than 4 pixels, do black
            for x, y in component:
                matrix[x, y] = 1

    components = find_components()
    # Step 1: Check if the matrix is already connected
    if len(components) <= 1:
        return matrix  # Already connected
    
    # Step 3: Find bordering 1s that can connect the components
    # Loop over all pairs of components and attempt to connect them
    while len(components) > 1:
        component_boarders = [find_bordering_ones(component) for component in components]
        # Get the first disconnected component
        print(len(components))
        best_pair = None
        min_distance = 10000
        for c1 in component_boarders:
            for c2 in component_boarders:
                if c1 != c2:
                    best_pair_, min_distance_ = find_min_lattice_distance_optimized(c1, c2)
                    if min_distance_ < min_distance:
                        best_pair = best_pair_
                        min_distance = min_distance_
        shortest_path = bresenham_line(best_pair[0][0], best_pair[0][1], best_pair[1][0], best_pair[1][1])
        for x, y in shortest_path:
            matrix[x, y] = 0
            for ii in range(path_width):
                new_x = x + ii - path_width // 2
                new_y = y + ii - path_width // 2
                new_x = 0 if new_x < 0 else new_x
                new_y = 0 if new_y < 0 else new_y
                new_x = max_x - 1 if new_x >= max_x else new_x
                new_y = max_y - 1 if new_y >= max_y else new_y
                matrix[new_x, new_y] = 0
        components = find_components() 
   
    return matrix


def create_stencil(image_path, do_plot=False, thick_factor=1, output_length=100):
    # Load the image

    try:
        image = cv2.imread(image_path)
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except:
        gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)


    # Apply Gaussian blur to smooth the image (optional but recommended for stencil effect)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Use edge detection (Canny algorithm)
    edges = cv2.Canny(blurred_image, threshold1=50, threshold2=150)

    # Invert the edges so that lines are black and background is white
    stencil = cv2.bitwise_not(edges)    
    _, stencil = cv2.threshold(stencil, 250, 255, cv2.THRESH_BINARY)

    if thick_factor > 1:
        # Create a kernel (structuring element) based on the factor 'x'
        kernel = np.ones((thick_factor, thick_factor), np.uint8)

        # Apply dilation to thicken the lines
        stencil = 255 - cv2.dilate(255 - stencil, kernel, iterations=1)

    if output_length is not None:
        output_width = int(output_length * stencil.shape[0] / stencil.shape[1])
        # Resize the image to the lower resolution
        stencil = cv2.resize(stencil, (output_width, output_length), interpolation=cv2.INTER_AREA)
        _, stencil = cv2.threshold(stencil, 250, 255, cv2.THRESH_BINARY)

    if do_plot:
        plt.figure(figsize=(6, 6))
        plt.imshow(stencil, cmap='gray')
        plt.title('Stencil Image')
        plt.axis('off')
        plt.show()        
    return stencil


def stencil_to_connected(image,  path_width=1, do_plot=False):
    zero_ones = (image < 255 / 2).astype(int)
    connected = zeroones_to_connected(zero_ones,  path_width, False)
    connected = (1 - connected) * 255
    if do_plot:
        plt.figure(figsize=(6, 6))
        plt.imshow(connected, cmap='gray')
        plt.title('Stencil Image')
        plt.axis('off')
        plt.show()      
    return connected    

def zeroones_to_connected(zero_ones,  path_width=1, do_plot=False):
    connected = connect_all_zeros(zero_ones, path_width)
    if do_plot:
        plt.figure(figsize=(6, 6))
        plt.imshow(connected, cmap='gray')
        plt.title('Stencil Image')
        plt.axis('off')
        plt.show()       
    return connected

def image_to_zeroones(image_path,grayscale_output_path=None, invert=True, scale_longer_side=400):
    img = Image.open(image_path).convert('L')  # Convert to grayscale

    if img.size[0] < img.size[1]:
        img_width = scale_longer_side
        img_height = int(img.size[0] *1.0 / img.size[1] * img_width)
    else :
        img_height = scale_longer_side
        img_width = int(img.size[1] *1.0 / img.size[0] * img_height)

    img = img.resize((img_height, img_width))  # Resize to 400x400 pixels


    # Save the grayscale image if an output path is provided
    if grayscale_output_path:
        img.save(grayscale_output_path)

    # Convert image to numpy array
    img_array = np.array(img)

    # Normalize the image array
    if invert:
        img_array = 1.0 - img_array / 255.0

    val_thresh = img_array.max() * 0.7

    # Flip the image array along the y-axis to correct mirroring
    # img_array = np.flipud(img_array)
    img_array = (img_array > val_thresh) * 1.0 
    return img_array    

def make_ones_bigger(matrix):
    new_matrix = copy.copy(matrix)
    for ii in range(matrix.shape[0]):
        for jj in range(matrix.shape[1]):
            if matrix[ii, jj] == 1:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_ii = ii + dx
                    new_jj = jj + dy
                    if new_ii >=0 and new_ii < matrix.shape[0] and new_jj >=0 and new_jj < matrix.shape[1]:
                        new_matrix[new_ii, new_jj] = 1
    return new_matrix

if __name__ == "__main__":
    # Example usage

    # x1, y1 = 0, 0  # Start point
    # x2, y2 = 7, 5  # End point

    # path = bresenham_line(x1, y1, x2, y2)
    # print("Path of points from ({}, {}) to ({}, {}):".format(x1, y1, x2, y2))
    # for point in path:
    #     print(point)    
    
    # matrix = np.array([
    #     [1, 1, 1, 1, 1],
    #     [1, 0, 0, 0, 1],
    #     [1, 0, 1, 0, 1],
    #     [1, 0, 0, 0, 1],
    #     [1, 1, 1, 1, 1]
    # ])

    # matrix = 1 - matrix

    # updated_matrix = connect_all_zeros(matrix)
    # print(updated_matrix)

    # updated_matrix = connect_all_zeros(updated_matrix)
    # print(updated_matrix)


    image_path = "~/Downloads/N26.jpg"
    stencil = create_stencil(image_path, thick_factor=5, do_plot=True, output_length=200)
    # print(stencil.shape)
    connected = stencil_to_connected(stencil, path_width=5, do_plot=True)
