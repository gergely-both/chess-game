from ..color_model import Color
from .figure import Figure
from ..board_model_view import Square, figures_squares_now


from itertools import chain


class King(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, target_square, positions_dict):
        """validates king moves: single move OR castling (short or long: user-selected non-offensive)"""
        initial = positions_dict[self].numerically
        target = target_square.numerically
        if abs(target.x - initial.x) <= 1 and abs(target.y - initial.y) <= 1:
            return True
        elif (
            self == self.game_instance.chosen_figure
            and abs(target.x - initial.x) == 2
            and target.y - initial.y == 0
        ):
            if self.game_instance.chosen_figure not in chain(*self.game_instance.log):
                if Figure.king_in_safety(
                    target_square=self.game_instance.initial_square
                ):
                    if target.x > initial.x:
                        castle_midpoint_square = Square.alphabetically(
                            (target.x - 1, target.y)
                        )
                        if self.game_instance.chosen_figure.color == Color.WHITE:
                            if (
                                "white_rook_2" not in chain(*self.game_instance.log)
                                and "white_rook_2" in positions_dict
                            ):
                                rook_position_num = figures_squares_now[
                                    "white_rook_2"
                                ].numerically
                        elif self.game_instance.chosen_figure.color == Color.BLACK:
                            if (
                                "black_rook_2" not in chain(*self.game_instance.log)
                                and "black_rook_2" in positions_dict
                            ):
                                rook_position_num = figures_squares_now[
                                    "black_rook_2"
                                ].numerically
                        else:
                            return False
                    elif target.x < initial.x:
                        castle_midpoint_square = Square.alphabetically(
                            (target.x + 1, target.y)
                        )
                        if self.game_instance.chosen_figure.color == Color.WHITE:
                            if (
                                "white_rook_1" not in chain(*self.game_instance.log)
                                and "white_rook_1" in positions_dict
                            ):
                                rook_position_num = figures_squares_now[
                                    "white_rook_1"
                                ].numerically
                        elif self.game_instance.chosen_figure.color == Color.BLACK:
                            if (
                                "black_rook_1" not in chain(*self.game_instance.log)
                                and "black_rook_1" in positions_dict
                            ):
                                rook_position_num = figures_squares_now[
                                    "black_rook_1"
                                ].numerically
                        else:
                            return False

                    if self.passage_free(initial, rook_position_num, positions_dict):
                        if Figure.king_in_safety(target_square=castle_midpoint_square):
                            return True
