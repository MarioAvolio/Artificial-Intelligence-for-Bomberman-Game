import copy
from threading import RLock, Thread
from time import sleep

from languages.predicate import Predicate
from application.settings_ import Settings
from application.model import dependance


class Game:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Game.__instance is None:
            Game()
        return Game.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Game.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__player = Player(0, 0)
            self.__enemy = Enemy(15, 0)
            self.__map = [[1, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [4, 0, 0, 0, 0, 0, 4, 4, 0, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 4, 0, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [4, 0, 0, 0, 3, 0, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [2, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
            self.__size = len(self.__map)
            Settings.BLOCK_SIZE = Settings.SIZE // self.__size
            self.__lock = RLock()
            Game.__instance = self
            self.__finish = None

    def outBorders(self, i: int, j: int) -> bool:
        with self.__lock:
            return i < 0 or j < 0 or i >= self.__size or j >= self.__size

    def __swap(self, oldI: int, oldJ: int, newI: int, newJ: int):
        self.__map[oldI][oldJ], self.__map[newI][newJ] = \
            self.__map[newI][newJ], \
            self.__map[oldI][oldJ]

    def plantBomb(self, i: int, j: int):
        with self.__lock:
            if self.getFinish() is not None:
                return

            if Movements.collision(i, j):
                return

            self.__writeElement(i, j, Settings.BOMB)
            # START THREAD BOMB
            Bomb(i, j).start()

    def moveOnMap(self, newPoint, oldPoint):
        with self.__lock:
            if self.getFinish() is not None:
                return

            self.__swap(oldPoint.getI(), oldPoint.getJ(), newPoint.getI(), newPoint.getJ())

    def explode(self, listPoints, coordinateBomb):
        with self.__lock:
            if self.getFinish() is not None:
                return

            # remove bomb
            self.__writeElement(coordinateBomb.getI(), coordinateBomb.getJ(), Settings.GRASS)

            for point in listPoints:  # adjacent point
                if not self.outBorders(point.getI(), point.getJ()):
                    if self.getElement(point.getI(), point.getJ()) == Settings.ENEMY:
                        self.__finish = "Player"  # player win
                    elif self.getElement(point.getI(), point.getJ()) == Settings.PLAYER:
                        self.__finish = "Enemy"  # enemy win
                    elif not Movements.collisionBomb(point.getI(), point.getJ()):
                        self.__writeElement(point.getI(), point.getJ(), Settings.GRASS)

    # SETTER
    def __writeElement(self, i: int, j: int, elem):
        with self.__lock:
            self.__map[i][j] = elem

    # GETTER
    def getElement(self, i: int, j: int):
        with self.__lock:
            return self.__map[i][j]

    def getPlayer(self):
        with self.__lock:
            return self.__player

    def getEnemy(self):
        with self.__lock:
            return self.__enemy

    def getSize(self):
        with self.__lock:
            return self.__size

    def getFinish(self):
        with self.__lock:
            return self.__finish


class Movements:

    @staticmethod
    def collision(i: int, j: int) -> bool:
        return Game.getInstance().outBorders(i, j) or Game.getInstance().getElement(i, j) != Settings.GRASS

    @staticmethod
    def collisionBomb(i: int, j: int) -> bool:
        return Game.getInstance().outBorders(i, j) or Game.getInstance().getElement(i, j) == Settings.BLOCK

    @staticmethod
    def move(direction: int, point):
        oldPoint = copy.deepcopy(point)

        if direction in dependance.MOVEMENTS_MATRIX.keys():
            point.move(direction)

        if Movements.collision(point.getI(), point.getJ()):
            point.setI(oldPoint.getI())
            point.setJ(oldPoint.getJ())
        else:
            Game.getInstance().moveOnMap(point, oldPoint)

    @staticmethod
    def plant():
        i = Game.getInstance().getPlayer().getI() + dependance.lastMovement[Point.I]
        j = Game.getInstance().getPlayer().getJ() + dependance.lastMovement[Point.J]
        Game.getInstance().plantBomb(i, j)


class Point(Predicate):
    predicate_name = "point"
    I = 0
    J = 1

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i"), ("j")])
        self.__coordinate = [i, j]  # list

    def getI(self):
        return self.__coordinate[Point.I]

    def getJ(self):
        return self.__coordinate[Point.J]

    def setI(self, i: int):
        self.__coordinate[Point.I] = i

    def setJ(self, j: int):
        self.__coordinate[Point.J] = j

    def move(self, direction: int):
        if direction in dependance.MOVEMENTS_MATRIX.keys():
            self.__coordinate[Point.I] += dependance.MOVEMENTS_MATRIX[direction][Point.I]
            self.__coordinate[Point.J] += dependance.MOVEMENTS_MATRIX[direction][Point.J]

    def __str__(self):
        return f"Point({self.__coordinate[Point.I]}, {self.__coordinate[Point.J]}) \n"


class Player(Point):
    def __init__(self, i: int, j: int):
        super().__init__(i, j)


class Enemy(Point):
    def __init__(self, i: int, j: int):
        super().__init__(i, j)


class Bomb(Thread, Point):
    def __init__(self, i: int, j: int):
        Thread.__init__(self)
        Point.__init__(self, i, j)
        self.__listPoints = [Point(i, j) for _ in range(4)]
        self.__listPoints[0].move(dependance.LEFT)
        self.__listPoints[1].move(dependance.RIGHT)
        self.__listPoints[2].move(dependance.UP)
        self.__listPoints[3].move(dependance.DOWN)

    def run(self) -> None:
        sleep(2)  # time to explode bomb
        Game.getInstance().explode(self.__listPoints, self)
