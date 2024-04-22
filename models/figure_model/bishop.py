from .figure import Figure

class Bishop(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, target_square, positions_dict):
        """validates bishop moves"""
        initial = positions_dict[self].numerically
        target = target_square.numerically
        return abs(target.x - initial.x) == abs(
            target.y - initial.y
        ) and self.passage_free(initial, target, positions_dict)