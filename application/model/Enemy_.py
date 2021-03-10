from application.model.Point_ import Point


class Enemy(Point):
    def __init__(self, i: int, j: int):
        super().__init__(i, j)
