import chess_utils.board_view as bv
from enum import Enum
from itertools import cycle, chain


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
        self.numerically = NumberedEquivalent(bv.numeric_equivalent[name[0]], int(name[1]))

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
        if detected_piece:
            enemy_piece = detected_piece if (detected_piece.color != self.color) else None
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

for square, coordinates in bv.squares_and_coordinates.items():
    central_coordinates = bv.square_centers[square]
    square_names_objs[square] = Square(square, coordinates, central_coordinates)

for piece in bv.pieces_and_positions:
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

for piece, position in bv.pieces_and_positions.items():
    figure = figure_names_objs[piece]
    square = square_names_objs[position]
    figures_squares_orig[figure] = square
figures_squares_now = figures_squares_orig.copy()


