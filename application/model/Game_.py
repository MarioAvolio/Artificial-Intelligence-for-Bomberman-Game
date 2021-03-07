from threading import RLock

from application import Settings_
from application.model.Bomb_ import Bomb
from application.model.Enemy_ import Enemy
from application.model.Movements_ import Movements
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
            self.lock = RLock()
            Game.__instance = self

    def outBorders(self, i: int, j: int) -> bool:
        return i < 0 or j < 0 or i >= self.__size or j >= self.__size

    def __swap(self, oldI, oldJ, newI, newJ):
        self.__map[oldI][oldJ], self.__map[newI][newJ] = \
            self.__map[newI][newJ], \
            self.__map[oldI][oldJ]

    def plantBomb(self, i: int, j: int) -> bool:
        with self.lock:
            if Movements.collision(i, j):
                return False

            self.writeElement(i, j, Settings_.BOMB)
            # START THREAD BOMB
            Bomb(i, j).start()

            return True

    def moveOnMap(self, newPoint: Point, oldPoint: Point):
        with self.lock:
            self.__swap(oldPoint.getI(), oldPoint.getJ(), newPoint.getI(), newPoint.getJ())

    def explode(self, listPoints):
        with self.lock:
            for point in listPoints:
                if self.getElement(point.getI(), point.getJ()) == Settings_.ENEMY:
                    pass  # win
                elif self.getElement(point.getI(), point.getJ()) == Settings_.PLAYER:
                    pass  # game over
                elif not Movements.collision(point.getI(), point.getJ()):
                    self.writeElement(point.getI(), point.getJ(), Settings_.GRASS)

    # SETTER
    def writeElement(self, i: int, j: int, elem):
        with self.lock:
            self.__map[i][j] = elem

    # GETTER
    def getElement(self, i: int, j: int):
        with self.lock:
            return self.__map[i][j]

    def getPlayer(self):
        return self.__player

    def getEnemy(self):
        return self.__enemy

    def getSize(self):
        return self.__size
