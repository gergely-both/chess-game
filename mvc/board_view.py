from .chess_model import (
    Square,
    figures_squares_orig,
    figures_squares_now,
    TILE_LENGTH,
    TILES_PER_SIDE,
    LIGHT_COLOR,
    DARK_COLOR,
    RESOURCE_PATH,
    Figure,
)

import tkinter as tk
import os


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
                target_square, figures_squares_now, game_instance
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
