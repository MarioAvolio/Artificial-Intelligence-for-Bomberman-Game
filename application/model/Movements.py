import copy

from application.Settings import Settings
from application.model.Game import Game


class Movements:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    def __init__(self):
        pass

    @staticmethod
    def collision(i: int, j: int) -> bool:
        return Game.getInstance().outBorders(i, j) or Game.getInstance().getMap()[i][j] != Settings.GRASS

    @staticmethod
    def move(mov: int, point):
        oldPoint = copy.deepcopy(point)
        if mov == Movements.LEFT:
            point.moveLeft()
        elif mov == Movements.RIGHT:
            point.moveRight()
        elif mov == Movements.UP:
            point.moveUp()
        elif mov == Movements.DOWN:
            point.moveDown()

        if Movements.collision(point.getI(), point.getJ()):
            point.setI(oldPoint.getI())
            point.setJ(oldPoint.getJ())
        else:
            Game.getInstance().moveOnMap(point, oldPoint)
