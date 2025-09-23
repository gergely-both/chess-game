from ..color_model import Color
from ..board_model_view import Square, figures_squares_now

from itertools import cycle


class Figure:
    def __init__(self, color, kind, name, number):
        self.color: Color = color
        self.kind: str = kind
        self.name: str = name
        self.number: int = number

        board_instance = None
        game_instance = None

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
            xy = list(
                zip(cycle([target.x]), y)
                if len(x) < len(y)
                else zip(x, cycle([target.y]))
            )
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
            enemy_piece = (
                detected_piece if (detected_piece.color != self.color) else None
            )
            return enemy_piece

    @classmethod
    def king_in_safety(cls, target_square):
        """checks if piece move to target square threatens own king; special case: castling"""
        chosen_figure = cls.game_instance.chosen_figure
        projected_positions = figures_squares_now.copy()

        attacked_piece = chosen_figure.detect_enemy(target_square)
        if attacked_piece and attacked_piece in projected_positions:
            del projected_positions[attacked_piece]
        projected_positions[chosen_figure] = target_square

        if chosen_figure.color == Color.WHITE:
            for figure in projected_positions:
                if figure.color == Color.BLACK:
                    if figure.validate_move(
                        projected_positions["white_king_1"], projected_positions
                    ):
                        return False
        elif chosen_figure.color == Color.BLACK:
            for figure in projected_positions:
                if figure.color == Color.WHITE:
                    if figure.validate_move(
                        projected_positions["black_king_1"], projected_positions
                    ):
                        return False
        return True
