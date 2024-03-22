#########################################
# VIEW
#########################################


from chess_utils.board_parameters import RESOURCE_PATH, TILES_PER_SIDE, TILE_LENGTH, DARK_COLOR, LIGHT_COLOR
from chess_utils.board_model import square_names_objs, figures_squares_now, figures_squares_orig, Figure, Square
from chess_utils.board_controller import Game
import tkinter as tk
import os


class Board:
    """board type for creating board display with figures overlaid; click detector, shows/hides possible moves"""
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
        # TODO: make pngs resizable by parameters, 
        self.img_files = os.listdir(RESOURCE_PATH)
        self.imgname_relpath = {os.path.splitext(k)[0]: RESOURCE_PATH + k for k in self.img_files}
        for img in self.imgname_relpath:
            setattr(self, img, tk.PhotoImage(file=self.imgname_relpath[img]))
        for figure, square in figures_squares_orig.items():  
            setattr(self, str(figure), self.canvas.create_image(square.central_coordinates, image=getattr(self, figure.name)))

        board_instance = None
        game_instance = None

        
    def click(self, event, game_instance):
        # TODO: make click bound to specific instances instead whole classes, if viable (to make multi-window display possible)
        """binds board and game instances to other types for mutual reference; dispatches to controller section"""
        Board.board_instance = self
        Board.game_instance = game_instance
        Game.board_instance = self
        Game.game_instance = game_instance
        Figure.board_instance = self
        Figure.game_instance = game_instance
        Square.board_instance = self
        Square.game_instance = game_instance

        selected_coordinates = event.x, event.y
        game_instance.select_square(selected_coordinates)

        
    def show_possibilities(self):
        # NOTE: is bound to instance and class
        """makes possibility-showing canvas objects and their IDs"""
        possible_squares = []
        for square, obj in square_names_objs.items():
            target_square = obj

            if self.game_instance.chosen_figure.validate_move(target_square, figures_squares_now):
                if Figure.king_in_safety(target_square):
                    if Square.square_not_owned(target_square):
                        origo = target_square.central_coordinates
                        radius = TILE_LENGTH // 8
                        fill = "green" if self.game_instance.turn % 2 != 0 else "purple"
                        setattr(self, square, self.canvas.create_oval(origo[0] - radius, origo[1] - radius, origo[0] + radius, origo[1] + radius, fill=fill))
                        possible_squares.append(target_square)
                        self.game_instance.enpass_enemy = None

        if not possible_squares:
            self.game_instance.chosen_figure = None
            self.game_instance.initial_square = None

            
    def hide_possibilities(self):
        """removes possibility-showing canvas objects by their IDs"""
        for square in square_names_objs:
            try:
                self.canvas.delete(getattr(self, str(square)))
            except AttributeError:
                continue

