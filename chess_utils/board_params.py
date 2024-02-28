import string

# chess board design
TILES_PER_SIDE = 8
TILE_LENGTH = 100  # pixels
DARK_COLOR = "#1b262c"
LIGHT_COLOR = "#0f4c75"

# square names with all their coordinates
squares_and_coordinates = {}
for x in range(TILES_PER_SIDE):
    for y in range(TILES_PER_SIDE):
        tile_id = string.ascii_lowercase[:TILES_PER_SIDE][x] + string.digits[TILES_PER_SIDE:0:-1][y]
        tile_coordinates = [(xb, yb) for xb in range(x * TILE_LENGTH, (x + 1) * TILE_LENGTH) for yb in range(y * TILE_LENGTH, (y + 1) * TILE_LENGTH)]
        squares_and_coordinates[tile_id] = tile_coordinates

# square names with their central coordinates
square_centers = {}
for square in squares_and_coordinates:
    coordinates = (squares_and_coordinates[square][0][0] + TILE_LENGTH // 2, squares_and_coordinates[square][0][1] + TILE_LENGTH // 2)
    square_centers[square] = coordinates


# piece names with their starting positions
pieces_and_positions = {
    "white_pawn_1": "a2",
    "white_pawn_2": "b2",
    "white_pawn_3": "c2",
    "white_pawn_4": "d2",
    "white_pawn_5": "e2",
    "white_pawn_6": "f2",
    "white_pawn_7": "g2",
    "white_pawn_8": "h2",
    "white_rook_1": "a1",
    "white_knight_1": "b1",
    "white_bishop_1": "c1",
    "white_queen_1": "d1",
    "white_king_1": "e1",
    "white_bishop_2": "f1",
    "white_knight_2": "g1",
    "white_rook_2": "h1",
    "black_pawn_1": "a7",
    "black_pawn_2": "b7",
    "black_pawn_3": "c7",
    "black_pawn_4": "d7",
    "black_pawn_5": "e7",
    "black_pawn_6": "f7",
    "black_pawn_7": "g7",
    "black_pawn_8": "h7",
    "black_rook_1": "a8",
    "black_knight_1": "b8",
    "black_bishop_1": "c8",
    "black_queen_1": "d8",
    "black_king_1": "e8",
    "black_bishop_2": "f8",
    "black_knight_2": "g8",
    "black_rook_2": "h8",
}

# starting positions copy for later reference
starting_positions = pieces_and_positions.copy()

# chess board squares name forms
numeric_equivalent = {letter: number for number, letter in enumerate(string.ascii_lowercase[:TILES_PER_SIDE], start=1)}
lettered_equivalent = {number: letter for number, letter in enumerate(string.ascii_lowercase[:TILES_PER_SIDE], start=1)}
