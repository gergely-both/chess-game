from .figure import Figure

class Knight(Figure):
    def __init__(self, color, kind, name, number):
        super().__init__(color, kind, name, number)

    def validate_move(self, target_square, positions_dict):
        """validates knight moves"""
        initial = positions_dict[self].numerically
        target = target_square.numerically
        return (
            abs(target.x - initial.x) in {1, 2}
            and abs(target.x - initial.x) + abs(target.y - initial.y) == 3
        )
