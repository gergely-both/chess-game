#########################################
# VIEW
#########################################

# TODO: king in safety move to upper class, click system revise, make pngs resizable by param, 

from chess_utils.board_params import RESOURCE_PATH, TILES_PER_SIDE, TILE_LENGTH, DARK_COLOR, LIGHT_COLOR
from chess_utils.board_model import square_names_objs, figures_squares_now, figures_squares_orig, Figure, Square
import tkinter as tk
import os


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
        for figure, square in figures_squares_orig.items():  
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

            if game.chosen_figure.validate_move(game.initial_square, target_square, figures_squares_now) and Figure.king_in_safety(game.chosen_figure, target_square) and Square.square_not_owned(target_square):
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

