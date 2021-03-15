import copy
import os
from threading import RLock, Thread
from time import sleep

from languages.asp.asp_input_program import ASPInputProgram
from languages.asp.asp_mapper import ASPMapper
from languages.predicate import Predicate
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

from application import dependance
from application.settings_ import Settings


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
            initializeASP()
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

            self.__swap(oldPoint.get_i(), oldPoint.get_j(), newPoint.get_i(), newPoint.get_j())

    def explode(self, listPoints, coordinateBomb):
        with self.__lock:
            if self.getFinish() is not None:
                return

            # remove bomb
            self.__writeElement(coordinateBomb.get_i(), coordinateBomb.get_j(), Settings.GRASS)

            for point in listPoints:  # adjacent point
                if not self.outBorders(point.get_i(), point.get_j()):
                    if self.getElement(point.get_i(), point.get_j()) == Settings.ENEMY:
                        self.__finish = "Player"  # player win
                    elif self.getElement(point.get_i(), point.get_j()) == Settings.PLAYER:
                        self.__finish = "Enemy"  # enemy win
                    elif not Movements.collisionBomb(point.get_i(), point.get_j()):
                        self.__writeElement(point.get_i(), point.get_j(), Settings.GRASS)

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

        recallASP()
        oldPoint = copy.deepcopy(point)

        if direction in dependance.MOVEMENTS_MATRIX.keys():
            point.move(direction)

        if Movements.collision(point.get_i(), point.get_j()):
            point.set_i(oldPoint.get_i())
            point.set_j(oldPoint.get_j())
        else:
            Game.getInstance().moveOnMap(point, oldPoint)

    @staticmethod
    def plant():
        i = Game.getInstance().getPlayer().get_i() + dependance.lastMovement[Point.I]
        j = Game.getInstance().getPlayer().get_j() + dependance.lastMovement[Point.J]
        Game.getInstance().plantBomb(i, j)


class Point(Predicate):
    predicate_name = "point"
    I = 0
    J = 1

    def __init__(self, i=None, j=None, type=None):
        Predicate.__init__(self, [("i", int), ("j", int), ("type", int)])
        self.__coordinate = [i, j]  # list
        self.__type = type

    def get_i(self):
        return self.__coordinate[Point.I]

    def get_j(self):
        return self.__coordinate[Point.J]

    def get_type(self):
        return self.__type

    def set_type(self, type: int):
        self.__type = type

    def set_i(self, i: int):
        self.__coordinate[Point.I] = i

    def set_j(self, j: int):
        self.__coordinate[Point.J] = j

    def move(self, direction: int):
        if direction in dependance.MOVEMENTS_MATRIX.keys():
            self.__coordinate[Point.I] += dependance.MOVEMENTS_MATRIX[direction][Point.I]
            self.__coordinate[Point.J] += dependance.MOVEMENTS_MATRIX[direction][Point.J]

    def __str__(self):
        return f"Point({self.__coordinate[Point.I]}, {self.__coordinate[Point.J]}) \n"


class Player(Point):
    def __init__(self, i: int, j: int):
        super().__init__(i, j, Settings.PLAYER)


class Enemy(Point):
    def __init__(self, i: int, j: int):
        super().__init__(i, j, Settings.ENEMY)


def getDistanceEP(p1: Point, e1: Point):
    PI = p1.get_i()
    PJ = p1.get_j()
    EI = e1.get_i()
    EJ = e1.get_j()

    print((pow(pow(EI - PI, 2) + pow(EJ - PJ, 2), 1 / 2)).float.as_integer_ratio())
    return (pow(pow(EI - PI, 2) + pow(EJ - PJ, 2), 1 / 2)).float.as_integer_ratio()


def computeNeighbors(i: int, j: int):
    listPoints = [Point(i, j) for _ in range(4)]
    listPoints[0].move(dependance.LEFT)
    listPoints[1].move(dependance.RIGHT)
    listPoints[2].move(dependance.UP)
    listPoints[3].move(dependance.DOWN)

    return listPoints


class Bomb(Thread, Point):
    def __init__(self, i: int, j: int):
        Thread.__init__(self)
        Point.__init__(self, i, j)
        self.__listPoints = computeNeighbors(i, j)

    def run(self) -> None:
        sleep(2)  # time to explode bomb
        Game.getInstance().explode(self.__listPoints, self)

global handler
global fixedInputProgram
fixedInputProgram = ASPInputProgram()
global variableInputProgram
variableInputProgram = ASPInputProgram()


def initializeASP():
    try:
        global handler
        handler = DesktopHandler(DLV2DesktopService(os.path.join(Settings.resource_path, "../../lib/DLV2.exe")))
        ASPMapper.get_instance().register_class(Point)
        fixedInputProgram.add_files_path(os.path.join(Settings.resource_path, "rules.dlv2"))
        for elem in range(6):
            fixedInputProgram.add_program(f"elem({elem}).")

        handler.add_program(fixedInputProgram)

    except Exception as e:
        print("exception")
        print(str(e))


def recallASP():
    try:
        variableInputProgram.clear_all()  # clear at each call

        # Example facts: point(I, J, ELEMENT_TYPE)
        # input matrix as facts
        size = Game.getInstance().getSize()
        for i in range(size):
            for j in range(size):
                typeNumber = Game.getInstance().getElement(i, j)
                variableInputProgram.add_program(f"cell({i},{j},{typeNumber}).")
                # print(f"cell({i},{j},{typeNumber}).", end=' ')

        # print()

        # compute neighbors values
        e = Game.getInstance().getEnemy()
        p = Game.getInstance().getPlayer()

        listAdjacent = computeNeighbors(e.get_i(), e.get_j())
        for adjacent in listAdjacent:
            if not Game.getInstance().outBorders(adjacent.get_i(), adjacent.get_j()):
                variableInputProgram.add_program(
                    f"distance({adjacent.get_i()}, {adjacent.get_j()}, {getDistanceEP(adjacent, p)}).")
                print(f"distance({adjacent.get_i()}, {adjacent.get_j()}, {getDistanceEP(adjacent, p)}).")

        handler.add_program(variableInputProgram)
        answerSets = handler.start_sync()

        # for answerSet in answerSets.get_optimal_answer_sets():
        # print(answerSet.get_atoms())


    except Exception as e:
        print("exception")
        print(str(e))
