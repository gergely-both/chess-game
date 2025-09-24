from .chess_model import (
    TILE_LENGTH,
    Square,
    figures_squares_now,
    square_names_objs,
    Color,
    Figure,
    Rook,
    Bishop,
    Queen,
    Knight,
)

import tkinter as tk


class Game:
    """game type for controlling gui interactions by the model rules"""

    def __init__(self):
        self.turn = 1
        self.chosen_figure = None
        self.initial_square = None
        self.attacked_figure = None
        self.enpass_enemy = None
        self.promote_piece = None
        self.promote_at = None
        self.log = []

    def detect_turn(self):
        """returns current turn's color"""
        if self.turn % 2 == 0:
            return Color.BLACK
        else:
            return Color.WHITE

    def choosing_piece(self, selected_square):
        """selects figure to move OR attack"""
        if detected_figure := Figure.detect_figure(selected_square):
            if self.detect_turn() is detected_figure.color:
                self.initial_square = selected_square
                self.chosen_figure = detected_figure
                return True
            elif self.chosen_figure:
                self.attacked_figure = detected_figure

    def select_square(self, selected_coordinates, board_instance):
        """main cycle of game mechanics dispatcher system"""
        selected_square = Square.detect_square(selected_coordinates)
        if self.chosen_figure:  # target square clicked
            target_square = selected_square
            board_instance.hide_possibilities()
            if not self.choosing_piece(
                selected_square
            ):  # target is to move to, not own piece reselection
                if self.chosen_figure.validate_move(
                    target_square, figures_squares_now, self
                ):  # if target is legit
                    if Figure.king_in_safety(target_square, self):
                        self.make_move(target_square, board_instance)
                        self.write_to_log(target_square)
                        self.turn += 1  # turn ended
            self.reset_choices()
        elif self.choosing_piece(selected_square):
            board_instance.show_possibilities(
                self
            )  # tells board instance the game instance

    def promote_to(self, img_name, query_window, board_instance):
        """references figure to promote, its destination, and the desired new figure object"""
        del figures_squares_now[self.promote_piece]
        board_instance.canvas.delete(getattr(board_instance, str(self.promote_piece)))

        new_piece_attrs = img_name.split("_")
        new_piece_color, new_piece_kind = new_piece_attrs[0], new_piece_attrs[1]
        new_piece_name = new_piece_color + "_" + new_piece_kind

        occupied_numbers = []
        for figure in figures_squares_now:
            if figure.name == new_piece_name:
                occupied_numbers.append(figure.number)
        new_piece_number = max(occupied_numbers) + 1

        if new_piece_kind == "rook":
            new_piece = Rook(
                Color[new_piece_color.upper()],
                new_piece_kind,
                new_piece_name,
                new_piece_number,
            )
        elif new_piece_kind == "bishop":
            new_piece = Bishop(
                Color[new_piece_color.upper()],
                new_piece_kind,
                new_piece_name,
                new_piece_number,
            )
        elif new_piece_kind == "queen":
            new_piece = Queen(
                Color[new_piece_color.upper()],
                new_piece_kind,
                new_piece_name,
                new_piece_number,
            )
        elif new_piece_kind == "knight":
            new_piece = Knight(
                Color[new_piece_color.upper()],
                new_piece_kind,
                new_piece_name,
                new_piece_number,
            )

        if self.promote_at:
            setattr(
                board_instance,
                str(new_piece),
                board_instance.canvas.create_image(
                    self.promote_at.central_coordinates,
                    image=getattr(board_instance, img_name),
                ),
            )
            figures_squares_now[new_piece] = self.promote_at
            self.promote_piece = None
            self.promote_at = None
            query_window.destroy()

    def reset_choices(self):
        self.chosen_figure = None
        self.initial_square = None
        self.attacked_figure = None
        self.enpass_enemy = None

    def write_to_log(self, target_square):
        self.log.append(
            [
                self.turn,
                str(self.chosen_figure),
                str(self.initial_square),
                str(target_square),
            ]
        )

    def make_move(self, target_square, board_instance):
        """removes captured figure from positions db, makes move, sends to promotion, does castling"""
        initial = self.initial_square.numerically if self.initial_square else None
        target = target_square.numerically
        if initial and target:
            x = (target.x - initial.x) * TILE_LENGTH
            y = (initial.y - target.y) * TILE_LENGTH
            if self.attacked_figure:
                del figures_squares_now[self.attacked_figure]
                board_instance.canvas.delete(
                    getattr(board_instance, str(self.attacked_figure))
                )
            elif self.enpass_enemy:
                del figures_squares_now[self.enpass_enemy]
                board_instance.canvas.delete(
                    getattr(board_instance, str(self.enpass_enemy))
                )
            board_instance.canvas.move(
                getattr(board_instance, str(self.chosen_figure)), x, y
            )
            figures_squares_now[self.chosen_figure] = target_square

            if self.chosen_figure and (
                (self.chosen_figure.name == "white_pawn" and target.y == 8)
                or (self.chosen_figure.name == "black_pawn" and target.y == 1)
            ):
                promotion_query = tk.Toplevel()
                promotion_query.title("*PROMOTION*")
                tk.Label(
                    master=promotion_query, text="Select the promotion grade: "
                ).grid(column=1, row=0, columnspan=2)
                counter = 0
                for img_name in board_instance.imgname_relpath:
                    if "pawn" not in img_name and "king" not in img_name:
                        if (
                            self.chosen_figure.color == Color.WHITE
                            and "white" in img_name
                        ) or (
                            self.chosen_figure.color == Color.BLACK
                            and "black" in img_name
                        ):
                            tk.Button(
                                master=promotion_query,
                                image=getattr(board_instance, img_name),
                                command=lambda img_name=img_name: self.promote_to(
                                    img_name, promotion_query, board_instance
                                ),  # creates buttons for figures to promote to
                            ).grid(column=counter, row=1)
                            counter += 1
                self.promote_piece = self.chosen_figure
                self.promote_at = target_square

            elif (
                str(self.chosen_figure) == "white_king_1"
                and abs(target.x - initial.x) == 2
            ):
                if target.x - initial.x == 2:
                    board_instance.canvas.move(
                        board_instance.white_rook_2, -2 * TILE_LENGTH, 0
                    )
                    figures_squares_now["white_rook_2"] = square_names_objs["f1"]
                elif target.x - initial.x == -2:
                    board_instance.canvas.move(
                        board_instance.white_rook_1, 3 * TILE_LENGTH, 0
                    )
                    figures_squares_now["white_rook_1"] = square_names_objs["d1"]
            elif (
                str(self.chosen_figure) == "black_king_1"
                and abs(target.x - initial.x) == 2
            ):
                if target.x - initial.x == 2:
                    board_instance.canvas.move(
                        board_instance.black_rook_2, -2 * TILE_LENGTH, 0
                    )
                    figures_squares_now["black_rook_2"] = square_names_objs["f8"]
                elif target.x - initial.x == -2:
                    board_instance.canvas.move(
                        board_instance.black_rook_1, 3 * TILE_LENGTH, 0
                    )
                    figures_squares_now["black_rook_1"] = square_names_objs["d8"]
