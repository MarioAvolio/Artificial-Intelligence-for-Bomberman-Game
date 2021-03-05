from application.model.Point import Point


class Player(Point):
    def __init__(self, i: int, j: int):
        super().__init__(i, j)
