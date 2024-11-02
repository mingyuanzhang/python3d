import trimesh
from trimesh.creation import box, cylinder


# connector.show()

scale = 0.9

board_height = 200 * scale
board_width = 200 * scale
board_thickness = 3

hole_radius = 10
hole_position = board_height / 2 - hole_radius - 10

pocket_height = 100 * scale
pocket_thickness = 30
pocket_width = board_width - 2 * hole_radius * 2 - 10 * 2

board = box(extents=[board_height, board_width, board_thickness])

hole1 = cylinder(radius=hole_radius, height=board_thickness)
hole1.apply_translation([hole_position, hole_position, 0])
board = board.difference(hole1)

hole1 = cylinder(radius=hole_radius, height=board_thickness)
hole1.apply_translation([hole_position, -hole_position, 0])
board = board.difference(hole1)

hole1 = cylinder(radius=hole_radius, height=board_thickness)
hole1.apply_translation([-hole_position, hole_position, 0])
board = board.difference(hole1)

hole1 = cylinder(radius=hole_radius, height=board_thickness)
hole1.apply_translation([-hole_position, -hole_position, 0])
board = board.difference(hole1)

pocket_bottom = box(extents = [pocket_width, board_thickness, pocket_thickness])
pocket_bottom.apply_translation([0, (board_width - board_thickness) / 2 * (-1), pocket_thickness/2+board_thickness/2])

board = board.union(pocket_bottom)

pocket_left = box(extents = [board_thickness, pocket_height - board_thickness, pocket_thickness])
pocket_left.apply_translation([-(pocket_width - board_thickness) / 2, (pocket_height - board_thickness) / 2 * (-1), pocket_thickness/2+board_thickness/2])
board = board.union(pocket_left)

pocket_right = box(extents = [board_thickness, pocket_height - board_thickness, pocket_thickness])
pocket_right.apply_translation([+(pocket_width - board_thickness) / 2, (pocket_height - board_thickness) / 2 * (-1), pocket_thickness/2+board_thickness/2])
board = board.union(pocket_right)

pocket_cover = box(extents = [pocket_width, pocket_height, board_thickness])
pocket_cover.apply_translation([0, (board_width - pocket_height) / 2 * (-1), pocket_thickness+board_thickness/2])
board = board.union(pocket_cover)

connector = trimesh.load("../stls/StraightTwoScrews.stl")
bounding_box = connector.bounds
top_edge = bounding_box[1][1]
connector = connector.apply_translation([0, (board_height / 2 - top_edge), -board_thickness/2])

board = board.union(connector)

# board.show()

board.export("~/Downloads/fencemount.stl")