from threading import Thread
from time import sleep

from application.model.Point_ import Point


class Bomb(Thread):
    def __init__(self, i: int, j: int):
        super().__init__()
        from application.model.Movements_ import Movements
        self.__coordinate = Point(i, j)
        self.__listPoints = [Point(i, j) for _ in range(4)]
        self.__listPoints[0].move(Movements.LEFT)
        self.__listPoints[1].move(Movements.RIGHT)
        self.__listPoints[2].move(Movements.UP)
        self.__listPoints[3].move(Movements.DOWN)

    def run(self) -> None:
        from application.model.Game_ import Game

        sleep(2)  # time to explode bomb
        Game.getInstance().explode(self.__listPoints, self.__coordinate)
