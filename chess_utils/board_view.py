#########################################
# VIEW
#########################################

#TODO: make figure pngs size by params, 

import string
import tkinter as tk
import os


RESOURCE_PATH = "chess_pieces/"
square_names_objs = {}
figures_squares_now = {}


# chess board design
TILES_PER_SIDE = 8
TILE_LENGTH = 100 # pixels
DARK_COLOR = "#1b262c"
LIGHT_COLOR = "#0f4c75"

# square names with all their coordinates
squares_and_coordinates = {}
for x in range(TILES_PER_SIDE):
    for y in range(TILES_PER_SIDE):
        tile_ID = string.ascii_lowercase[:TILES_PER_SIDE][x] + string.digits[TILES_PER_SIDE:0:-1][y]
        tile_coordinates = [(xb, yb) for xb in range(x * TILE_LENGTH, (x + 1) * TILE_LENGTH) for yb in range(y * TILE_LENGTH, (y + 1) * TILE_LENGTH)]
        squares_and_coordinates[tile_ID] = tile_coordinates

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


class Board:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game")
        self.master.geometry(f"{TILES_PER_SIDE * TILE_LENGTH}x{TILES_PER_SIDE * TILE_LENGTH}")
        self.master.resizable(False, False)
        self.canvas = tk.Canvas(master=master, width=TILES_PER_SIDE * TILE_LENGTH, height=TILES_PER_SIDE * TILE_LENGTH, highlightthickness=0)

        for i in range(0, TILES_PER_SIDE*TILE_LENGTH, 2*TILE_LENGTH):
            for j in range(0, TILES_PER_SIDE*TILE_LENGTH, 2*TILE_LENGTH):
                for k in range(0, TILES_PER_SIDE*TILE_LENGTH, TILE_LENGTH):
                    self.canvas.create_rectangle(i+k, j+k, TILE_LENGTH+i+k, TILE_LENGTH+j+k, fill=LIGHT_COLOR)
                    self.canvas.create_rectangle((TILES_PER_SIDE*TILE_LENGTH)-i-k, j+k, ((TILES_PER_SIDE-1)*TILE_LENGTH)-i-k, TILE_LENGTH+j+k, fill=DARK_COLOR)
        
        self.canvas.pack()

        self.img_files = os.listdir(RESOURCE_PATH)
        self.imgname_relpath = {os.path.splitext(k)[0]: RESOURCE_PATH + k for k in self.img_files}
        for img in self.imgname_relpath:
            setattr(self, img, tk.PhotoImage(file=self.imgname_relpath[img]))
        for figure, square in figures_squares_now.items():  
            setattr(self, str(figure), self.canvas.create_image(square.central_coordinates, image=getattr(self, figure.name)))

        self.game_instance = None

    def click(self, event, game):
        """makes contact between types for mutual reference; sends GUI event to controller"""
        self.game_instance = game
        Figure.game_instance = game
        Square.game_instance = game
        game.board_instance = self

        selected_coordinates = event.x, event.y
        game.select_square(selected_coordinates)

    def show_possibilities(self):
        """makes possibility-showing canvas objects and their IDs"""
        game = self.game_instance
        possible_squares = []
        for square, obj in square_names_objs.items():
            target_square = obj

            if game.chosen_figure.validate_move(game.initial_square, target_square, figures_squares_now) and King.in_safety(game.chosen_figure, target_square) and Square.square_not_owned(target_square):
                origo = target_square.central_coordinates
                radius = TILE_LENGTH // 8
                fill = "green" if game.turn % 2 != 0 else "purple"
                setattr(self, square, self.canvas.create_oval(origo[0] - radius, origo[1] - radius, origo[0] + radius, origo[1] + radius, fill=fill))
                possible_squares.append(target_square)
                game.enpass_enemy = None
        if not possible_squares:
            game.chosen_figure = None
            game.initial_square = None

    def hide_possibilities(self):
        """removes possibility-showing canvas objects by their IDs"""
        for square in square_names_objs:
            try:
                self.canvas.delete(getattr(self, str(square)))
            except AttributeError:
                continue


