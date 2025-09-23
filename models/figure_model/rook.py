from . import Figure


class Rook(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, target_square, positions_dict, game_instance):
        """validates rook moves"""
        initial = positions_dict[self].numerically
        target = target_square.numerically
        return (
            target.x - initial.x == 0 or target.y - initial.y == 0
        ) and self.passage_free(initial, target, positions_dict)
