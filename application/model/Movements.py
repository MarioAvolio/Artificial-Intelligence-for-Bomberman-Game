from application.Settings import Settings
from application.model.Game import Game
from application.model.Point import Point


class Movements:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    def __init__(self):
        self.game = Game()

    def collision(self, i: int, j: int):
        return self.game.getMap()[i][j] != Settings.GRASS or self.game.outBorders(i, j)

    def move(self, mov: int, point: Point):
        oldI = point.getI()
        oldJ = point.getJ()
        
        if mov == Movements.LEFT:
