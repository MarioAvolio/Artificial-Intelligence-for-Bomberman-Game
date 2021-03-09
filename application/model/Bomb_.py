from threading import Thread
from time import sleep

from application.model.Point_ import Point


class Bomb(Thread):
    def __init__(self, i: int, j: int):
        super().__init__()
        self.__coordinate = Point(i, j)
        from application.model.Movements_ import Movements
        self.__listPoints = [Point(i, j) for _ in range(4)]
        self.__listPoints[0].move(Movements.LEFT)
        self.__listPoints[1].move(Movements.RIGHT)
        self.__listPoints[2].move(Movements.UP)
        self.__listPoints[3].move(Movements.DOWN)

    def run(self) -> None:
        print("run")
        sleep(2)
        print("aspetto il lock")
        from application.model.Game_ import Game
        Game.getInstance().explode(self.__listPoints, self.__coordinate)
