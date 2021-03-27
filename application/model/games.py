import copy
import datetime
import os
from threading import Thread, RLock
from time import sleep

import pygame
# === CONSTANS === (UPPER_CASE names)
from languages.asp.asp_input_program import ASPInputProgram
from languages.asp.asp_mapper import ASPMapper
from languages.predicate import Predicate
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SIZE = 800

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

lastMovement = MOVEMENTS_MATRIX[RIGHT]
movements = {
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_DOWN: DOWN,
    pygame.K_UP: UP
}

GRASS = 0
PLAYER = 1
ENEMY = 2
BLOCK = 3
BOX = 4
BOMB = 5

current_path = os.path.dirname(__file__)  # Where your .py file is located
resource_path = os.path.join(current_path, '../resources')  # The resource folder path
logs_path = os.path.join(resource_path, 'logs')

BLOCK_SIZE = 50


# === CLASSES === (CamelCase names)

class Point:
    I = 0
    J = 1

    def __init__(self, i: int, j: int):
        self._coordinate = [i, j]  # list

    def get_i(self):
        return self._coordinate[Point.I]

    def get_j(self):
        return self._coordinate[Point.J]

    def set_i(self, i: int):
        self._coordinate[Point.I] = i

    def set_j(self, j: int):
        self._coordinate[Point.J] = j

    def move(self, directions: int):
        if directions in MOVEMENTS_MATRIX.keys():
            self._coordinate[Point.I] += MOVEMENTS_MATRIX[directions][Point.I]
            self._coordinate[Point.J] += MOVEMENTS_MATRIX[directions][Point.J]

    def __str__(self):
        return f"Point [{self._coordinate[Point.I]}, {self._coordinate[Point.J]}]."

    def __key(self):
        return self.get_i(), self.get_j()

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.__key() == other.__key()
        return NotImplemented

    def __hash__(self):
        return hash(self.__key())


class Game:
    def __init__(self):
        self.__player = PointType(0, 0, PLAYER)
        self.__enemy = PointType(15, 0, ENEMY)
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

        # self.__map = dlvThread.dlv.getMatrix()
        # print(self.__map)
        self.__size = len(self.__map)
        global BLOCK_SIZE
        BLOCK_SIZE = SIZE // self.__size
        self.__lock = RLock()
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

            if collision(i, j):
                return

            self.__writeElement(i, j, BOMB)
            # START THREAD BOMB
            Bomb(i, j).start()

    def moveOnMap(self, newPoint: Point, oldPoint: Point):
        with self.__lock:
            if self.getFinish() is not None:
                return

            self.__swap(oldPoint.get_i(), oldPoint.get_j(), newPoint.get_i(), newPoint.get_j())

    def moveEnemy(self, point: Point):
        with self.__lock:
            self.moveOnMap(point, self.__enemy)
            self.__enemy.set_j(point.get_j())
            self.__enemy.set_i(point.get_i())

    def explode(self, listPoints, coordinateBomb):
        with self.__lock:
            if self.getFinish() is not None:
                return

            # remove bomb
            self.__writeElement(coordinateBomb.get_i(), coordinateBomb.get_j(), GRASS)

            for point in listPoints:  # adjacent point
                if not self.outBorders(point.get_i(), point.get_j()):
                    if self.getElement(point.get_i(), point.get_j()) == ENEMY:
                        self.__finish = "Player"  # player win
                    elif self.getElement(point.get_i(), point.get_j()) == PLAYER:
                        self.__finish = "Enemy"  # enemy win
                    elif not collisionBomb(point.get_i(), point.get_j()):
                        self.__writeElement(point.get_i(), point.get_j(), GRASS)

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


class PointType(Point):

    def __init__(self, i: int, j: int, t: int):
        Point.__init__(self, i, j)
        self.__t = t

    def get_t(self):
        return self.__t

    def set_t(self, t: int):
        self.__t = t


class InputPointType(Predicate, PointType):
    predicate_name = "point"

    def __init__(self, i, j, t):
        Predicate.__init__(self, [("i", int), ("j", int), ("t", int)])
        PointType.__init__(self, i, j, t)


class Bomb(Thread, PointType):
    TIME_LIMIT = 5

    def __init__(self, i: int, j: int):
        PointType.__init__(self, i, j, BOMB)
        Thread.__init__(self)
        self.__listPoints = computeNeighbors(i, j)

    def run(self) -> None:
        sleep(Bomb.TIME_LIMIT)  # time to explode bomb
        gameInstance.explode(self.__listPoints, self)


class EnemyBomb(Predicate, Point):
    predicate_name = "enemybomb"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class NoEnemyBomb(Predicate, Point):
    predicate_name = "noenemybomb"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class InputBomb(Predicate, Point):
    predicate_name = "bomb"

    def __init__(self, i=None, j=None):
        Point.__init__(self, i, j)
        Predicate.__init__(self, [("i", int), ("j", int)])


class NoPath(Predicate, Point):
    predicate_name = "nopath"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class Path(Predicate, Point):
    predicate_name = "path"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class AdjacentPlayerAndEnemy(Predicate, Point):
    predicate_name = "adjacentPlayerAndEnemy"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class Distance(Predicate, Point):
    predicate_name = "distance"

    def __init__(self, i=None, j=None, d=None):
        Predicate.__init__(self, [("i", int), ("j", int), ("d", int)])
        Point.__init__(self, i, j)
        self.d = d

    def get_d(self):
        return self.d

    def set_d(self, d: int):
        self.d = d


class HandlerView:
    def __init__(self):
        # PATH
        terrainPath = os.path.join(resource_path, "terrain")

        # IMG DICTIONARY
        self.__imgdictionary = {}

        # IMG TERRAIN
        img = pygame.image.load(os.path.join(terrainPath, "block.png"))
        self.__imgdictionary[BLOCK] = pygame.transform.scale(img,
                                                             (BLOCK_SIZE, BLOCK_SIZE))

        img = pygame.image.load(os.path.join(terrainPath, "box.png"))
        self.__imgdictionary[BOX] = pygame.transform.scale(img, (BLOCK_SIZE, BLOCK_SIZE))

        img = pygame.image.load(os.path.join(terrainPath, "grass.png"))
        self.__imgdictionary[GRASS] = pygame.transform.scale(img,
                                                             (BLOCK_SIZE, BLOCK_SIZE))

        # IMG BOMBERMAN
        img = pygame.image.load(os.path.join(resource_path, "bomberman.png"))
        self.__imgdictionary[PLAYER] = pygame.transform.scale(img,
                                                              (BLOCK_SIZE, BLOCK_SIZE))

        # IMG ENEMY
        img = pygame.image.load(os.path.join(resource_path, "enemy.png"))
        self.__imgdictionary[ENEMY] = pygame.transform.scale(img,
                                                             (BLOCK_SIZE, BLOCK_SIZE))

        # IMG BOMB
        img = pygame.image.load(os.path.join(resource_path, "bomb.png"))
        self.__imgdictionary[BOMB] = pygame.transform.scale(img,
                                                            (BLOCK_SIZE, BLOCK_SIZE))

        # BACKGROUND
        img = pygame.image.load(os.path.join(resource_path, "background.jpg"))
        self.__imgBackground = pygame.transform.scale(img, (SIZE, SIZE))

    def __printOnScreen(self, surface):
        if gameInstance.getFinish() is None:
            for i in range(gameInstance.getSize()):
                for j in range(gameInstance.getSize()):

                    if gameInstance.getElement(i, j) in self.__imgdictionary.keys():
                        img = self.__imgdictionary[gameInstance.getElement(i, j)]
                        surface.blit(img, (j * BLOCK_SIZE, i * BLOCK_SIZE))
        else:
            self.__gameOver(surface)

        pygame.display.update()

    def update(self, surface):
        self.__printOnScreen(surface)

    def __gameOver(self, surface):
        surface.blit(self.__imgBackground, (0, 0))
        X = SIZE // 2
        Y = SIZE // 2
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(f"{gameInstance.getFinish()} Win!", True, GREEN, BLUE)
        textRect = text.get_rect()
        textRect.center = (X, Y)
        surface.blit(text, textRect)


# --- AI ---

class DLVSolution:

    def __init__(self):
        self.__countLogs = 0
        self.__dir = None
        self.__lastPositionsEnemy = {}
        self.__bombs = []
        self.__nMovements = 0
        try:
            self.__handler = DesktopHandler(
                DLV2DesktopService(os.path.join(resource_path, "../../lib/DLV2.exe")))
            ASPMapper.get_instance().register_class(InputPointType)
            ASPMapper.get_instance().register_class(Path)
            ASPMapper.get_instance().register_class(NoPath)
            ASPMapper.get_instance().register_class(Distance)
            ASPMapper.get_instance().register_class(InputBomb)
            ASPMapper.get_instance().register_class(EnemyBomb)
            ASPMapper.get_instance().register_class(NoEnemyBomb)
            ASPMapper.get_instance().register_class(AdjacentPlayerAndEnemy)

            self.__matrix = self.calculateMatrix()
            # print(self.__matrix)

            self.__fixedInputProgram = ASPInputProgram()
            self.__variableInputProgram = None

            self.__fixedInputProgram.add_files_path(os.path.join(resource_path, "enemyRules.dlv2"))
            self.__handler.add_program(self.__fixedInputProgram)

        except Exception as e:
            print(str(e))
    #
    # def getMatrix(self):
    #     return self.__matrix

    def calculateMatrix(self):
        h = DesktopHandler(
            DLV2DesktopService(os.path.join(resource_path, "../../lib/DLV2.exe")))
        ASPMapper.get_instance().register_class(InputPointType)
        matrixInputProgram = ASPInputProgram()
        matrixInputProgram.add_files_path(os.path.join(resource_path, "map.dlv2"))
        index = h.add_program(matrixInputProgram)
        answerSets = h.start_sync()
        matrix = [[0 for x in range(SIZE)] for y in range(SIZE)]

        print("~~~~~~~~~~~~~~~~~~~~~~  MATRIX ~~~~~~~~~~~~~~~~~~~~~~")
        for answerSet in answerSets.get_optimal_answer_sets():
            print(answerSet)
            for obj in answerSet.get_atoms():
                if isinstance(obj, InputPointType):
                    matrix[obj.get_i()][obj.get_j()] = obj.get_t()

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return matrix

    # DEBUG

    def __log_program(self):
        if not os.path.exists(logs_path):
            os.mkdir(f"{logs_path}")
        if self.__countLogs == 0:
            timestamp = datetime.datetime.now()
            self.__dir = f"{timestamp.hour}-{timestamp.minute}-{timestamp.second}"
            os.mkdir(f"{logs_path}/{self.__dir}")
        with open(f"{logs_path}/{self.__dir}/BomberFriend-{self.__countLogs}.log", "w") as f:
            f.write(f"Variable: \n"
                    f"{self.__variableInputProgram.get_programs()} \n\n\n"
                    f"Fixed:\n"
                    f"{self.__fixedInputProgram.get_files_paths()}")
        self.__countLogs += 1

    # END DEBUG

    def recallASP(self):
        try:
            # self.__nMovements += 1  # increase movements
            size = gameInstance.getSize()
            self.__variableInputProgram = ASPInputProgram()

            # input matrix as facts
            for i in range(size):
                for j in range(size):
                    typeNumber = gameInstance.getElement(i, j)
                    p = InputPointType(i, j, typeNumber)
                    self.__variableInputProgram.add_object_input(p)  # point(I, J, ELEMENT_TYPE)

            # compute neighbors values ai
            e = gameInstance.getEnemy()
            p = gameInstance.getPlayer()

            listAdjacent = computeNeighbors(e.get_i(), e.get_j())
            for adjacent in listAdjacent:
                if not gameInstance.outBorders(adjacent.get_i(), adjacent.get_j()):
                    distance = getDistanceEP(adjacent, p)
                    d = Distance(adjacent.get_i(), adjacent.get_j(), distance)
                    self.__variableInputProgram.add_object_input(d)

            # adding last position
            if len(self.__lastPositionsEnemy) != 0:
                for enemy in self.__lastPositionsEnemy:
                    self.__variableInputProgram.add_program(
                        f"lastPositionEnemy({enemy.get_i()}, {enemy.get_j()}, {self.__lastPositionsEnemy[enemy]}).")

            # adding bombs ai
            for bomb in self.__bombs:
                print(f"bomba piazzata in {bomb}")
                self.__variableInputProgram.add_object_input(bomb)

            index = self.__handler.add_program(self.__variableInputProgram)
            answerSets = self.__handler.start_sync()

            movePath = None
            print("#######################################")
            for answerSet in answerSets.get_optimal_answer_sets():
                print(answerSet)
                for obj in answerSet.get_atoms():
                    if isinstance(obj, Path):
                        # print(f"Path {obj}")
                        movePath = obj
                    elif isinstance(obj, InputBomb):
                        if obj not in self.__bombs:
                            # print(f"Aggiungo bomba {obj}")
                            self.__bombs.append(obj)
                            CheckBomb(self.__bombs, obj).start()
                    elif isinstance(obj, EnemyBomb):
                        gameInstance.plantBomb(obj.get_i(), obj.get_j())
                    elif isinstance(obj, AdjacentPlayerAndEnemy):
                        self.__lastPositionsEnemy.clear()  # clear last enemy position because enemy find player

            print("#######################################")
            if movePath is not None:
                enemyLastPositionTmp = copy.deepcopy(gameInstance.getEnemy())
                if enemyLastPositionTmp not in self.__lastPositionsEnemy:
                    self.__lastPositionsEnemy[enemyLastPositionTmp] = 0
                else:
                    self.__lastPositionsEnemy[enemyLastPositionTmp] += 1
                gameInstance.moveEnemy(movePath)

            self.__log_program()
            self.__handler.remove_program_from_id(index)

        except Exception as e:
            print(str(e))


is_running = True


class DLVThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.dlv = DLVSolution()

    def run(self):
        while is_running and gameInstance.getFinish() is None:
            self.dlv.recallASP()
            sleep(0.5)


class CheckBomb(Thread):

    def __init__(self, listBomb=None, bomb=None):
        Thread.__init__(self)
        self.__bombs = listBomb
        self.__bomb = bomb

    def run(self) -> None:
        stop = False
        while not stop:
            if gameInstance.getElement(self.__bomb.get_i(), self.__bomb.get_j()) == GRASS:
                self.__bombs.remove(self.__bomb)
                stop = True
                print(f"STOP!")


# === FUNCTIONS === (lower_case names)

def getDistanceEP(p1: Point, e1: Point) -> int:
    PI = p1.get_i()
    PJ = p1.get_j()
    EI = e1.get_i()
    EJ = e1.get_j()

    return int(pow(pow(EI - PI, 2) + pow(EJ - PJ, 2), 1 / 2))


def computeNeighbors(i: int, j: int):
    listPoints = [Path(i, j) for _ in range(4)]
    listPoints[0].move(LEFT)
    listPoints[1].move(RIGHT)
    listPoints[2].move(UP)
    listPoints[3].move(DOWN)

    return listPoints


def collision(i: int, j: int) -> bool:
    return gameInstance.outBorders(i, j) or gameInstance.getElement(i, j) != GRASS


def collisionBomb(i: int, j: int) -> bool:
    return gameInstance.outBorders(i, j) or gameInstance.getElement(i, j) == BLOCK


def move(directions: int, point):
    oldPoint = copy.deepcopy(point)

    if directions in MOVEMENTS_MATRIX.keys():
        point.move(directions)

    if collision(point.get_i(), point.get_j()):
        point.set_i(oldPoint.get_i())
        point.set_j(oldPoint.get_j())
    else:
        gameInstance.moveOnMap(point, oldPoint)


def plant():
    i = gameInstance.getPlayer().get_i() + lastMovement[Point.I]
    j = gameInstance.getPlayer().get_j() + lastMovement[Point.J]
    gameInstance.plantBomb(i, j)


# === MAIN === (lower_case names)

# --- (global) variables ---
dlvThread = DLVThread()
gameInstance = Game()

# --- init ---

pygame.init()

screen = pygame.display.set_mode((SIZE, SIZE))
screen_rect = screen.get_rect()
pygame.display.set_caption('BomberFriends')
programIcon = pygame.image.load(os.path.join(resource_path, "icon.png"))
pygame.display.set_icon(programIcon)

# --- objects ---

handler = HandlerView()
dlvThread.start()

# --- mainloop ---

clock = pygame.time.Clock()

while is_running:

    # --- events ---

    for event in pygame.event.get():

        # --- global events ---

        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_running = False
            if event.key in movements:
                direction = movements[event.key]
                lastMovement = MOVEMENTS_MATRIX[direction]  # set last movement
                move(direction, gameInstance.getPlayer())
            elif event.key == pygame.K_SPACE:
                plant()

        # --- objects events ---

    # --- updates ---

    # --- draws ---

    screen.fill(BLACK)
    handler.update(screen)

    pygame.display.update()

    # --- FPS ---

    clock.tick(25)

# --- the end ---

pygame.quit()
