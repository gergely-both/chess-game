from . import Color
from . import Figure, King, Queen, Pawn, Rook, Knight, Bishop
from . import (
    TILE_LENGTH,
    TILES_PER_SIDE,
    LIGHT_COLOR,
    DARK_COLOR,
    RESOURCE_PATH,
    pieces_and_positions,
    squares_and_coordinates,
    square_centers,
    numeric_equivalent,
)

import tkinter as tk
import os
from collections import namedtuple


NumberedEquivalent = namedtuple("NumberedEquivalent", ["x", "y"])
square_names_objs = {}
figure_names_objs = {}
figures_squares_orig = {}
figures_squares_now = {}


class Square:

    all_existing_squares = set()

    def __init__(self, name, all_coordinates, central_coordinates):
        self.name = name
        self.all_coordinates = all_coordinates
        self.central_coordinates = central_coordinates
        self.numerically = NumberedEquivalent(numeric_equivalent[name[0]], int(name[1]))
        Square.all_existing_squares.add(self)

    def __repr__(self):
        return self.name

    @classmethod
    def alphabetically(cls, num_pair):
        """returns square name from numeric equivalent"""
        if len(num_pair) == 2:
            for obj in square_names_objs.values():
                if obj.numerically == num_pair:
                    return obj

    @classmethod
    def detect_square(cls, coordinates):
        """returns square object of clicked coordinates"""
        for obj in square_names_objs.values():
            if coordinates in obj.all_coordinates:
                return obj

    @classmethod
    def square_not_owned(cls, square, game_instance):
        """checks/scans if square is already occupied by own piece"""
        for dict_figure, dict_square in figures_squares_now.items():
            if (
                square is dict_square
                and dict_figure.color is game_instance.chosen_figure.color
            ):
                return False
        return True


class Board:
    """board type for creating board display with figures overlaid; click detector, shows/hides possible moves"""

    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game")
        self.master.geometry(
            f"{TILES_PER_SIDE * TILE_LENGTH}x{TILES_PER_SIDE * TILE_LENGTH}"
        )
        self.master.resizable(False, False)

        self.canvas = tk.Canvas(
            master=master,
            width=TILES_PER_SIDE * TILE_LENGTH,
            height=TILES_PER_SIDE * TILE_LENGTH,
            highlightthickness=0,
        )
        for i in range(0, TILES_PER_SIDE * TILE_LENGTH, 2 * TILE_LENGTH):
            for j in range(0, TILES_PER_SIDE * TILE_LENGTH, 2 * TILE_LENGTH):
                for k in range(0, TILES_PER_SIDE * TILE_LENGTH, TILE_LENGTH):
                    self.canvas.create_rectangle(
                        i + k,
                        j + k,
                        TILE_LENGTH + i + k,
                        TILE_LENGTH + j + k,
                        fill=LIGHT_COLOR,
                    )
                    self.canvas.create_rectangle(
                        (TILES_PER_SIDE * TILE_LENGTH) - i - k,
                        j + k,
                        ((TILES_PER_SIDE - 1) * TILE_LENGTH) - i - k,
                        TILE_LENGTH + j + k,
                        fill=DARK_COLOR,
                    )
        self.canvas.pack()
        self.img_files = os.listdir(RESOURCE_PATH)
        self.imgname_relpath = {
            os.path.splitext(k)[0]: RESOURCE_PATH + k for k in self.img_files
        }
        for img in self.imgname_relpath:
            setattr(self, img, tk.PhotoImage(file=self.imgname_relpath[img]))
        for figure, square in figures_squares_orig.items():
            setattr(
                self,
                str(figure),
                self.canvas.create_image(
                    square.central_coordinates, image=getattr(self, figure.name)
                ),
            )

    def click(self, event, game_instance):
        """sends user action values for analysis and feedback"""
        selected_coordinates = event.x, event.y
        game_instance.select_square(selected_coordinates, self)

    def show_possibilities(self, game_instance):
        """makes possibility-showing canvas objects and their IDs"""
        possible_squares = []
        for square in Square.all_existing_squares:
            target_square = square

            if game_instance.chosen_figure.validate_move(
                target_square, figures_squares_now
            ):
                if Figure.king_in_safety(target_square, game_instance):
                    if Square.square_not_owned(target_square, game_instance):
                        origo = target_square.central_coordinates
                        radius = TILE_LENGTH // 8
                        fill = "green" if game_instance.turn % 2 != 0 else "purple"
                        setattr(
                            self,
                            square.name,
                            self.canvas.create_oval(
                                origo[0] - radius,
                                origo[1] - radius,
                                origo[0] + radius,
                                origo[1] + radius,
                                fill=fill,
                            ),
                        )
                        possible_squares.append(target_square)
                        game_instance.enpass_enemy = None

        if not possible_squares:
            game_instance.chosen_figure = None
            game_instance.initial_square = None

    def hide_possibilities(self):
        """removes possibility canvas objects by ID"""
        for square in Square.all_existing_squares:
            try:
                self.canvas.delete(getattr(self, square.name))
            except AttributeError:
                continue


# GENERATING OBJECTS FROM STRINGS INTO MULTIPLE REFERENCE DICTS; SAVING COPY FOR STARTING LAYOUT
for square, coordinates in squares_and_coordinates.items():
    central_coordinates = square_centers[square]
    square_names_objs[square] = Square(square, coordinates, central_coordinates)

for piece in pieces_and_positions:
    attributes = piece.split("_")
    color, kind, number = attributes[0], attributes[1], int(attributes[2])
    name = color + "_" + kind
    if kind == "pawn":
        figure_names_objs[piece] = Pawn(Color[color.upper()], kind, name, number)
    elif kind == "king":
        figure_names_objs[piece] = King(Color[color.upper()], kind, name, number)
    elif kind == "rook":
        figure_names_objs[piece] = Rook(Color[color.upper()], kind, name, number)
    elif kind == "bishop":
        figure_names_objs[piece] = Bishop(Color[color.upper()], kind, name, number)
    elif kind == "queen":
        figure_names_objs[piece] = Queen(Color[color.upper()], kind, name, number)
    elif kind == "knight":
        figure_names_objs[piece] = Knight(Color[color.upper()], kind, name, number)

for piece, position in pieces_and_positions.items():
    figure = figure_names_objs[piece]
    square = square_names_objs[position]
    figures_squares_orig[figure] = square
figures_squares_now = figures_squares_orig.copy()
