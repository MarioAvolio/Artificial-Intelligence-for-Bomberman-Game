import copy

from application.Settings import Settings
from application.model.Game import Game


class Movements:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    reverse = {
        LEFT: RIGHT,
        RIGHT: LEFT,
        DOWN: UP,
        UP: DOWN
    }

    def __init__(self):
        pass

    @staticmethod
    def collision(i: int, j: int) -> bool:
        return Game().getMap()[i][j] != Settings.GRASS or Game().outBorders(i, j)

    @staticmethod
    def move(mov: int, point):
        oldPoint = copy.copy(point)
        if mov == Movements.LEFT:
            point.moveLeft()
        elif mov == Movements.RIGHT:
            point.moveRight()
        elif mov == Movements.UP:
            point.moveUp()
        elif mov == Movements.DOWN:
            point.moveDown()

        # if Movements.collision(point.getI(), point.getJ()):
        #     mov = Movements.reverse[mov]
        #     Movements.move(mov, point)  # reverse movement
        # else:
        Game().moveOnMap(point, oldPoint)
