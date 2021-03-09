import copy

from application.model.Game_ import Game


class Movements:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    MOVEMENTS_MATRIX = {  # MOVEMENTS ON THE MATRIX
        # tuples
        LEFT: (0, -1),
        RIGHT: (0, 1),
        UP: (-1, 0),
        DOWN: (1, 0)
    }

    def __init__(self):
        pass

    @staticmethod
    def collision(i: int, j: int) -> bool:
        from application.Settings_ import Settings
        return Game.getInstance().outBorders(i, j) or Game.getInstance().getElement(i, j) != Settings.GRASS

    @staticmethod
    def collisionBomb(i: int, j: int) -> bool:
        from application.Settings_ import Settings
        return Game.getInstance().outBorders(i, j) or Game.getInstance().getElement(i, j) == Settings.BLOCK

    @staticmethod
    def move(direction: int, point):
        oldPoint = copy.deepcopy(point)

        if direction in Movements.MOVEMENTS_MATRIX.keys():
            point.move(direction)

        if Movements.collision(point.getI(), point.getJ()):
            point.setI(oldPoint.getI())
            point.setJ(oldPoint.getJ())
        else:
            Game.getInstance().moveOnMap(point, oldPoint)

    @staticmethod
    def plant():
        from application.controller.MoveController import MoveController
        from application.model.Point_ import Point
        i = Game.getInstance().getPlayer().getI() + MoveController.lastMovement[Point.I]
        j = Game.getInstance().getPlayer().getJ() + MoveController.lastMovement[Point.J]
        Game.getInstance().plantBomb(i, j)
