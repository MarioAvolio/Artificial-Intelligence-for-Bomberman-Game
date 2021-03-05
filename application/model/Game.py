from application.Settings import Settings
from application.model.Enemy import Enemy
from application.model.Player import Player


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Game(Singleton):
    def __init__(self):
        self.size = 10
        self.__map = [[1, 0, 3, 0, 3, 0, 0, 0, 0, 3],
                      [0, 0, 3, 0, 3, 0, 0, 0, 0, 3],
                      [4, 0, 3, 0, 3, 0, 0, 4, 0, 3],
                      [0, 0, 3, 0, 3, 0, 0, 0, 0, 3],
                      [0, 0, 0, 0, 3, 0, 0, 0, 0, 3],
                      [4, 0, 3, 0, 3, 0, 4, 0, 0, 3],
                      [0, 0, 3, 0, 3, 0, 0, 0, 0, 3],
                      [0, 0, 3, 0, 3, 0, 0, 4, 0, 3],
                      [2, 0, 3, 0, 3, 0, 0, 0, 0, 3],
                      [0, 0, 3, 0, 3, 0, 0, 0, 0, 3]]

        Settings.BLOCK_SIZE = Settings.SIZE // self.size
        self.__player = Player(0, 0)
        self.__enemy = Enemy(8, 0)

    def __outBorders(self, i: int, j: int):
        return i <= 0 or j <= 0 or i >= self.size or j >= self.size

    def getMap(self):
        return self.__map
