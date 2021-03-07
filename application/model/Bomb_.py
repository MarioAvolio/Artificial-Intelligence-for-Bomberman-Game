from threading import Thread
from time import sleep

from application.model import Game_
from application.model.Point_ import Point


class Bomb(Thread):
    def __init__(self, i: int, j: int):
        super().__init__()
        self.__i = i
        self.__j = j

    def run(self) -> None:
        sleep(2)
        listPoints = [Point(self.__i + 1, self.__j),
                      Point(self.__i - 1, self.__j),
                      Point(self.__i, self.__j + 1),
                      Point(self.__i, self.__j - 1)]
        Game_.getInstance().explode(listPoints)
