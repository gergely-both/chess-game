import chess_utils.board_params as bp
import tkinter as tk
from collections import namedtuple
from enum import Enum
from itertools import cycle, chain
import os


RESOURCE_PATH = "chess_pieces/"
NumberedEquivalent = namedtuple("NumberedEquivalent", ["x", "y"])
square_names_objs = {}
figure_names_objs = {}
figures_squares_orig = {}
figures_squares_now = {}


#########################################
# MODEL
#########################################


class Square:
    def __init__(self, name, all_coordinates, central_coordinates):
        self.name = name
        self.all_coordinates = all_coordinates
        self.central_coordinates = central_coordinates
        self.numerically = NumberedEquivalent(bp.numeric_equivalent[name[0]], int(name[1]))

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
    def square_not_owned(cls, square):
        """checks/scans if square is already occupied by own piece"""
        for dict_figure, dict_square in figures_squares_now.items():
            if square is dict_square and dict_figure.color is cls.game_instance.chosen_figure.color:
                return False
        return True


class Color(Enum):
    BLACK = 0
    WHITE = 1


class Figure:
    def __init__(self, color, kind, name, number):
        self.color: Color = color
        self.kind: str = kind
        self.name: str = name
        self.number: int = number
    
    def __repr__(self):
        color = str(self.color).split(".")[1].lower()
        return f"{color}_{self.kind}_{self.number}"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return hash(self) == hash(other)

    def passage_free(self, initial, target, positions_dict):
        """checks/scans if any square between initial and target squares is occupied by any piece"""
        x = list(range(initial.x + 1, target.x) or range(initial.x - 1, target.x, -1))
        y = list(range(initial.y + 1, target.y) or range(initial.y - 1, target.y, -1))
        if x and y:
            xy = list(zip(x, y))
            for num_pair in xy:
                if Square.alphabetically(num_pair) in positions_dict.values():
                    return False
        elif x or y:
            xy = list(zip(cycle([target.x]), y) if len(x) < len(y) else zip(x, cycle([target.y])))
            for num_pair in xy:
                if Square.alphabetically(num_pair) in positions_dict.values():
                    return False
        return True

    @classmethod
    def detect_figure(cls, selected_square):
        """returns figure object on user-selected square object"""
        for figure, square in figures_squares_now.items():
            if selected_square is square:
                return figure

    def detect_enemy(self, selected_square):
        detected_piece = Figure.detect_figure(selected_square)
        enemy_piece = detected_piece if detected_piece.color != self.color else None
        return enemy_piece


class Pawn(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, initial_square, target_square, positions_dict):
        """validates pawn moves: by both colors, initial double move OR simple move, capturing simply OR en passant"""
        initial, target = initial_square.numerically, target_square.numerically
        if self.color == Color.WHITE:
            if initial.y == 2 and target.y == 4 and initial.x == target.x \
                    and target_square not in positions_dict.values() \
                    and self.passage_free(initial, target, positions_dict):
                return True
            elif initial.y >= 2 and target.y - initial.y == 1 and initial.x == target.x \
                    and target_square not in positions_dict.values():
                return True
            elif target.y - initial.y == 1 and abs(target.x - initial.x) == 1:
                if self.detect_enemy(target_square):
                    return True
                elif initial.y == 5:
                    enpass_location = Square.alphabetically((target.x, target.y - 1))
                    enpass_enemy = self.detect_enemy(enpass_location)
                    if enpass_enemy and isinstance(enpass_enemy, Pawn) and {enpass_enemy, str(figures_squares_orig[enpass_enemy])}.issubset(self.game_instance.log[-1]):
                        self.game_instance.enpass_enemy = enpass_enemy
                        return True
        elif self.color == Color.BLACK:
            if initial.y == 7 and target.y == 5 and initial.x == target.x \
                    and target_square not in positions_dict.values() and self.passage_free(initial, target, positions_dict):
                return True
            elif initial.y <= 7 and initial.y - target.y == 1 and initial.x == target.x \
                    and target_square not in positions_dict.values():
                return True
            elif initial.y - target.y == 1 and abs(target.x - initial.x) == 1:
                if self.detect_enemy(target_square):
                    return True
                elif initial.y == 4:
                    enpass_location = Square.alphabetically((target.x, target.y + 1))
                    enpass_enemy = self.detect_figure(enpass_location)
                    if enpass_enemy and isinstance(enpass_enemy, Pawn) and {enpass_enemy, str(figures_squares_orig[enpass_enemy])}.issubset(self.game_instance.log[-1]):
                        self.game_instance.enpass_enemy = enpass_enemy
                        return True


class King(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, initial_square, target_square, positions_dict):
        """validates king moves: single move OR castling (short or long: user-selected non-offensive)"""
        # NOTE: can not castle from check, through it (both checked below), nor into it (checked back in main cycle later), also entire passage must be free
        initial, target = initial_square.numerically, target_square.numerically
        if abs(target.x - initial.x) <= 1 and abs(target.y - initial.y) <= 1:
            return True
        elif self == self.game_instance.chosen_figure and abs(target.x - initial.x) == 2 and target.y - initial.y == 0:
            if self.game_instance.chosen_figure not in chain(*self.game_instance.log) and self.in_safety(self.game_instance.chosen_figure, target_square=self.game_instance.initial_square):
                if target.x > initial.x:
                    castle_midpoint_square = Square.alphabetically((target.x - 1, target.y))
                    if self.game_instance.chosen_figure.color == Color.WHITE and "white_rook_2" not in chain(*self.game_instance.log) and "white_rook_2" in positions_dict:
                        rook_position_num = figures_squares_now["white_rook_2"].numerically
                    elif self.game_instance.chosen_figure.color == Color.BLACK and "black_rook_2" not in chain(*self.game_instance.log) and "black_rook_2" in positions_dict:
                        rook_position_num = figures_squares_now["black_rook_2"].numerically
                    else:
                        return False
                elif target.x < initial.x:
                    castle_midpoint_square = Square.alphabetically((target.x + 1, target.y))
                    if self.game_instance.chosen_figure.color == Color.WHITE and "white_rook_1" not in chain(*self.game_instance.log) and "white_rook_1" in positions_dict:
                        rook_position_num = figures_squares_now["white_rook_1"].numerically
                    elif self.game_instance.chosen_figure.color == Color.BLACK and "black_rook_1" not in chain(*self.game_instance.log) and "black_rook_1" in positions_dict:
                        rook_position_num = figures_squares_now["black_rook_1"].numerically
                    else:
                        return False

                if self.passage_free(initial, rook_position_num, positions_dict) and self.in_safety(self.game_instance.chosen_figure, target_square=castle_midpoint_square):
                    return True

    @classmethod
    def in_safety(cls, chosen_figure, target_square):
        """checks if piece move to target square threatens own king"""
        projected_positions = figures_squares_now.copy()

        attacked_piece = chosen_figure.detect_enemy(target_square)
        if attacked_piece and attacked_piece in projected_positions:
            del projected_positions[attacked_piece]
        projected_positions[chosen_figure] = target_square

        if chosen_figure.color == Color.WHITE:
            for figure in projected_positions:
                if figure.color == Color.BLACK and figure.validate_move(projected_positions[figure], projected_positions["white_king_1"], projected_positions):
                    return False
        elif chosen_figure.color == Color.BLACK:
            for figure in projected_positions:
                if figure.color == Color.WHITE and figure.validate_move(projected_positions[figure], projected_positions["black_king_1"], projected_positions):
                    return False
        return True


class Rook(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, initial_square, target_square, positions_dict):
        """validates rook moves"""
        initial, target = initial_square.numerically, target_square.numerically
        return (target.x - initial.x == 0 or target.y - initial.y == 0) and self.passage_free(initial, target, positions_dict)


class Bishop(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, initial_square, target_square, positions_dict):
        """validates bishop moves"""
        initial, target = initial_square.numerically, target_square.numerically
        return abs(target.x - initial.x) == abs(target.y - initial.y) and self.passage_free(initial, target, positions_dict)


class Queen(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, initial_square, target_square, positions_dict):
        """validates queen moves"""
        initial, target = initial_square.numerically, target_square.numerically
        return ((target.x - initial.x == 0 or target.y - initial.y == 0) and self.passage_free(initial, target, positions_dict)) \
            or (abs(target.x - initial.x) == abs(target.y - initial.y) and self.passage_free(initial, target, positions_dict))


class Knight(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, initial_square, target_square, positions_dict):
        """validates knight moves"""
        initial, target = initial_square.numerically, target_square.numerically
        return abs(target.x - initial.x) in {1, 2} and abs(target.x - initial.x) + abs(target.y - initial.y) == 3


# GENERATING OBJECTS FROM STRINGS INTO MULTIPLE REFERENCE DICTS; SAVING COPY FOR STARTING LAYOUT

for square, coordinates in bp.squares_and_coordinates.items():
    central_coordinates = bp.square_centers[square]
    square_names_objs[square] = Square(square, coordinates, central_coordinates)

for piece in bp.pieces_and_positions:
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

for piece, position in bp.pieces_and_positions.items():
    figure = figure_names_objs[piece]
    square = square_names_objs[position]
    figures_squares_orig[figure] = square

figures_squares_now = figures_squares_orig.copy()


#########################################
# VIEW
#########################################

class Board:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game")
        self.master.geometry(f"{bp.TILES_PER_SIDE * bp.TILE_LENGTH}x{bp.TILES_PER_SIDE * bp.TILE_LENGTH}")
        self.master.resizable(False, False)
        self.canvas = tk.Canvas(master=master, width=bp.TILES_PER_SIDE * bp.TILE_LENGTH, height=bp.TILES_PER_SIDE * bp.TILE_LENGTH, highlightthickness=0)

        for i in range(0, bp.TILES_PER_SIDE*bp.TILE_LENGTH, 2*bp.TILE_LENGTH):
            for j in range(0, bp.TILES_PER_SIDE*bp.TILE_LENGTH, 2*bp.TILE_LENGTH):
                for k in range(0, bp.TILES_PER_SIDE*bp.TILE_LENGTH, bp.TILE_LENGTH):
                    self.canvas.create_rectangle(i+k, j+k, bp.TILE_LENGTH+i+k, bp.TILE_LENGTH+j+k, fill=bp.LIGHT_COLOR)
                    self.canvas.create_rectangle((bp.TILES_PER_SIDE*bp.TILE_LENGTH)-i-k, j+k, ((bp.TILES_PER_SIDE-1)*bp.TILE_LENGTH)-i-k, bp.TILE_LENGTH+j+k, fill=bp.DARK_COLOR)
        
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
                radius = bp.TILE_LENGTH // 8
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


#########################################
# CONTROLLER
#########################################

class Game:
    def __init__(self):
        self.board_instance = None
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

    def choose_piece(self, selected_square):
        """selects figure to move OR attack"""
        detected_figure = Figure.detect_figure(selected_square)
        if detected_figure:
            if self.detect_turn() is detected_figure.color:
                self.initial_square = selected_square
                self.chosen_figure = detected_figure
                return True
            elif self.chosen_figure:
                self.attacked_figure = detected_figure

    def select_square(self, selected_coordinates):
        """main cycle for selecting squares, pieces, showing options, validating then making moves, log and reset"""
        selected_square = Square.detect_square(selected_coordinates)
        if self.chosen_figure:
            self.board_instance.hide_possibilities()
            target_square = selected_square
            if not self.choose_piece(selected_square):
                if self.chosen_figure.validate_move(self.initial_square, target_square, figures_squares_now) \
                        and King.in_safety(self.chosen_figure, target_square):
                    self.make_move(target_square)
                    self.log.append([self.turn, str(self.chosen_figure), str(self.initial_square), str(target_square)])
                    self.turn += 1
            self.chosen_figure = None
            self.initial_square = None
            self.attacked_figure = None
            self.enpass_enemy = None
        elif self.choose_piece(selected_square):
            self.board_instance.show_possibilities()

    def promote_to(self, img_name, query_window):
        """references figure to promote, its destination, and the desired new figure object"""
        del figures_squares_now[self.promote_piece]
        self.board_instance.canvas.delete(getattr(self.board_instance, str(self.promote_piece)))
        
        new_piece_attrs = img_name.split("_")
        new_piece_color, new_piece_kind = new_piece_attrs[0], new_piece_attrs[1]
        new_piece_name = new_piece_color + "_" + new_piece_kind

        occupied_numbers = []
        for figure in figures_squares_now:
            if figure.name == new_piece_name:
                occupied_numbers.append(figure.number)
        new_piece_number = max(occupied_numbers) + 1

        if new_piece_kind == "rook":
            new_piece = Rook(Color[new_piece_color.upper()], new_piece_kind, new_piece_name, new_piece_number)
        elif new_piece_kind == "bishop":
            new_piece = Bishop(Color[new_piece_color.upper()], new_piece_kind, new_piece_name, new_piece_number)
        elif new_piece_kind == "queen":
            new_piece = Queen(Color[new_piece_color.upper()], new_piece_kind, new_piece_name, new_piece_number)
        elif new_piece_kind == "knight":
            new_piece = Knight(Color[new_piece_color.upper()], new_piece_kind, new_piece_name, new_piece_number)

        setattr(self.board_instance, str(new_piece), self.board_instance.canvas.create_image(self.promote_at.central_coordinates, image=getattr(self.board_instance, img_name)))
        figures_squares_now[new_piece] = self.promote_at

        self.promote_piece = None
        self.promote_at = None
        query_window.destroy()

    def make_move(self, target_square):
        """removes captured figure from positions db, makes move, sends to promotion, does castling"""
        initial, target = self.initial_square.numerically, target_square.numerically
        x = (target.x - initial.x) * bp.TILE_LENGTH
        y = (initial.y - target.y) * bp.TILE_LENGTH
        if self.attacked_figure:
            del figures_squares_now[self.attacked_figure]
            self.board_instance.canvas.delete(getattr(self.board_instance, str(self.attacked_figure)))
        elif self.enpass_enemy:
            del figures_squares_now[self.enpass_enemy]
            self.board_instance.canvas.delete(getattr(self.board_instance, str(self.enpass_enemy)))
        self.board_instance.canvas.move(getattr(self.board_instance, str(self.chosen_figure)), x, y)
        figures_squares_now[self.chosen_figure] = target_square

        if (self.chosen_figure.name == "white_pawn" and target.y == 8) or (self.chosen_figure.name == "black_pawn" and target.y == 1):
            promotion_query = tk.Toplevel()
            promotion_query.title("*PROMOTION*")
            tk.Label(master=promotion_query, text="Select the promotion grade: ").grid(column=1, row=0, columnspan=2)
            counter = 0
            for img_name in self.board_instance.imgname_relpath:
                if "pawn" not in img_name and "king" not in img_name:
                    if (self.chosen_figure.color == Color.WHITE and "white" in img_name) or (self.chosen_figure.color == Color.BLACK and "black" in img_name):
                        tk.Button(master=promotion_query, image=getattr(self.board_instance, img_name), command=lambda img_name=img_name: self.promote_to(img_name, promotion_query)).grid(column=counter, row=1)
                        counter += 1
            self.promote_piece = self.chosen_figure
            self.promote_at = target_square

        elif str(self.chosen_figure) == "white_king_1" and abs(target.x - initial.x) == 2:
            if target.x - initial.x == 2:
                self.board_instance.canvas.move(self.board_instance.white_rook_2, -2 * bp.TILE_LENGTH, 0)
                figures_squares_now["white_rook_2"] = square_names_objs["f1"]
            elif target.x - initial.x == -2:
                self.board_instance.canvas.move(self.board_instance.white_rook_1, 3 * bp.TILE_LENGTH, 0)
                figures_squares_now["white_rook_1"] = square_names_objs["d1"]
        elif str(self.chosen_figure) == "black_king_1" and abs(target.x - initial.x) == 2:
            if target.x - initial.x == 2:
                self.board_instance.canvas.move(self.board_instance.black_rook_2, -2 * bp.TILE_LENGTH, 0)
                figures_squares_now["black_rook_2"] = square_names_objs["f8"]
            elif target.x - initial.x == -2:
                self.board_instance.canvas.move(self.board_instance.black_rook_1, 3 * bp.TILE_LENGTH, 0)
                figures_squares_now["black_rook_1"] = square_names_objs["d8"]
