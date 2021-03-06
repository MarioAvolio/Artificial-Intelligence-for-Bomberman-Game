from application.Settings import Settings
from application.model.Enemy import Enemy
from application.model.Player import Player
from application.model.Point import Point


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Game(Singleton):
    def __init__(self):
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

        self.size = len(self.__map)
        Settings.BLOCK_SIZE = Settings.SIZE // self.size
        self.__player = Player(0, 0)
        self.__enemy = Enemy(15, 0)

    def outBorders(self, i: int, j: int) -> bool:
        return i <= 0 or j <= 0 or i >= self.size or j >= self.size

    def __swap(self, oldI, oldJ, newI, newJ):
        self.__map[oldI][oldJ], self.__map[newI][newJ] = self.__map[newI][newJ], self.__map[oldI][oldJ]

    def moveOnMap(self, newPoint: Point, oldPoint: Point):
        self.__swap(oldPoint.getI(), oldPoint.getJ(), newPoint.getI(), newPoint.getJ())
        print(f"new: {newPoint}")
        print(f"old: {oldPoint}")

    # GETTER
    def getMap(self):
        return self.__map

    def getPlayer(self):
        return self.__player

    def getEnemy(self):
        return self.__enemy
