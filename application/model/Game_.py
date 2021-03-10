from threading import RLock

from application.model.Bomb_ import Bomb
from application.model.Enemy_ import Enemy
from application.model.Player_ import Player
from application.model.Point_ import Point


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

            from application.model.Movements_ import Movements
            from application.Settings_ import Settings

            if Movements.collision(i, j):
                return

            self.__writeElement(i, j, Settings.BOMB)
            # START THREAD BOMB
            Bomb(i, j).start()

    def moveOnMap(self, newPoint: Point, oldPoint: Point):
        with self.__lock:
            if self.getFinish() is not None:
                return

            self.__swap(oldPoint.getI(), oldPoint.getJ(), newPoint.getI(), newPoint.getJ())

    def explode(self, listPoints, coordinateBomb: Point):
        with self.__lock:
            if self.getFinish() is not None:
                return

            from application.model.Movements_ import Movements
            from application.Settings_ import Settings

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
