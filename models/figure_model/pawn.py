from .figure import Figure
from ..board_model import Square, figures_squares_orig
from ..color_model import Color


class Pawn(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, target_square, positions_dict):
        """validates pawn moves: by both colors, initial double move OR simple move, capturing simply OR en passant"""
        initial = positions_dict[self].numerically
        target = target_square.numerically
        if self.color == Color.WHITE:
            if (
                initial.y == 2
                and target.y == 4
                and initial.x == target.x
                and target_square not in positions_dict.values()
                and self.passage_free(initial, target, positions_dict)
            ):
                return True
            elif (
                initial.y >= 2
                and target.y - initial.y == 1
                and initial.x == target.x
                and target_square not in positions_dict.values()
            ):
                return True
            elif target.y - initial.y == 1 and abs(target.x - initial.x) == 1:
                if self.detect_enemy(target_square):
                    return True
                elif initial.y == 5:
                    enpass_location = Square.alphabetically((target.x, target.y - 1))
                    enpass_enemy = self.detect_enemy(enpass_location)
                    if enpass_enemy and isinstance(enpass_enemy, Pawn):
                        if {
                            enpass_enemy,
                            str(figures_squares_orig[enpass_enemy]),
                        }.issubset(self.game_instance.log[-1]):
                            self.game_instance.enpass_enemy = enpass_enemy
                            return True
        elif self.color == Color.BLACK:
            if (
                initial.y == 7
                and target.y == 5
                and initial.x == target.x
                and target_square not in positions_dict.values()
                and self.passage_free(initial, target, positions_dict)
            ):
                return True
            elif (
                initial.y <= 7
                and initial.y - target.y == 1
                and initial.x == target.x
                and target_square not in positions_dict.values()
            ):
                return True
            elif initial.y - target.y == 1 and abs(target.x - initial.x) == 1:
                if self.detect_enemy(target_square):
                    return True
                elif initial.y == 4:
                    enpass_location = Square.alphabetically((target.x, target.y + 1))
                    enpass_enemy = self.detect_figure(enpass_location)
                    if enpass_enemy and isinstance(enpass_enemy, Pawn):
                        if {
                            enpass_enemy,
                            str(figures_squares_orig[enpass_enemy]),
                        }.issubset(self.game_instance.log[-1]):
                            self.game_instance.enpass_enemy = enpass_enemy
                            return True

