import copy
import datetime
import itertools
import os
import sys
from threading import Thread
from time import sleep
from typing import List

import pygame
# === CONSTANS === (UPPER_CASE names)
from languages.asp.asp_input_program import ASPInputProgram
from languages.asp.asp_mapper import ASPMapper
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

from application.model.lock import RWLock
from application.model.pointClass import *

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
ERROR = -1

current_path = os.path.dirname(__file__)  # Where your .py file is located
resource_path = os.path.join(current_path, '../resources')  # The resource folder path
logs_path = os.path.join(resource_path, 'logs')

BLOCK_SIZE = 50
MAP_SIZE = 16


# === CLASSES === (CamelCase names)


class Game:
    def __init__(self):
        self.__map = None
        self.__player = PointType(0, 0, PLAYER)
        self.__enemy = PointType(0, 1, ENEMY)
        self.__size = None
        self.lock = RWLock()
        self.__finish = None

    def outBorders(self, i: int, j: int) -> bool:
        return i < 0 or j < 0 or i >= self.__size or j >= self.__size

    def __swap(self, oldI: int, oldJ: int, newI: int, newJ: int):
        self.__map[oldI][oldJ], self.__map[newI][newJ] = \
            self.__map[newI][newJ], \
            self.__map[oldI][oldJ]

    def plantBomb(self, i: int, j: int):
        if self.getFinish() is not None:
            return

        if collision(i, j):
            print(self.getElement(i, j))
            return

        self.__writeElement(i, j, BOMB)
        # START THREAD BOMB
        BombThread(i, j).start()

    def moveOnMap(self, newPoint: Point, oldPoint: Point):
        if self.getFinish() is not None:
            return
            # print(f"swap {newPoint} and {oldPoint}")
        self.__swap(oldPoint.get_i(), oldPoint.get_j(), newPoint.get_i(), newPoint.get_j())

    def moveEnemy(self, point: Point):
        if self.getFinish() is not None:
            return
        # print(f"muovo il nemico in {point} dalla precedente posizione {self.__enemy}")
        self.moveOnMap(point, self.__enemy)
        self.__enemy.set_j(point.get_j())
        self.__enemy.set_i(point.get_i())

    def explode(self, listPoints: List[Point], coordinateBomb: Point):
        if self.getFinish() is not None:
            return

        for point in listPoints:  # adjacent point
            if not self.outBorders(point.get_i(), point.get_j()):
                if self.getElement(point.get_i(), point.get_j()) == ENEMY:
                    self.__finish = "Player"  # player win
                elif self.getElement(point.get_i(), point.get_j()) == PLAYER:
                    self.__finish = "Enemy"  # enemy win
                elif not collisionBomb(point.get_i(), point.get_j()):
                    self.__writeElement(point.get_i(), point.get_j(), GRASS)

            # remove bomb
        self.__writeElement(coordinateBomb.get_i(), coordinateBomb.get_j(), GRASS)

    # SETTER
    def __writeElement(self, i: int, j: int, elem):
        self.__map[i][j] = elem

    def setMap(self, w: List[List[int]]):
        self.__map = w
        self.__size = len(self.__map)
        global BLOCK_SIZE
        BLOCK_SIZE = SIZE // self.__size
        playerCoordinates = [(index, row.index(PLAYER)) for index, row in enumerate(self.__map) if
                             PLAYER in row]  # set player
        setCharacter(self.__player, playerCoordinates[0])

        enemyCoordinates = [(index, row.index(ENEMY)) for index, row in enumerate(self.__map) if
                            ENEMY in row]  # set enemy
        setCharacter(self.__enemy, enemyCoordinates[0])

    # GETTER
    def getElement(self, i: int, j: int) -> int:
        try:
            return self.__map[i][j]
        except Exception as e:
            return ERROR

    def getPlayer(self) -> Point:
        return self.__player

    def getEnemy(self) -> Point:
        return self.__enemy

    def getSize(self) -> int:
        return self.__size

    def getFinish(self) -> str:
        return self.__finish


class HandlerView:
    def __init__(self):
        # PATH
        terrainPath = os.path.join(resource_path, "terrain")

        # IMG DICTIONARY
        self.__imgDictionary = {}

        # IMG TERRAIN
        img = pygame.image.load(os.path.join(terrainPath, "block.png"))
        self.__imgDictionary[BLOCK] = pygame.transform.scale(img,
                                                             (BLOCK_SIZE, BLOCK_SIZE))

        img = pygame.image.load(os.path.join(terrainPath, "box.png"))
        self.__imgDictionary[BOX] = pygame.transform.scale(img, (BLOCK_SIZE, BLOCK_SIZE))

        img = pygame.image.load(os.path.join(terrainPath, "grass.png"))
        self.__imgDictionary[GRASS] = pygame.transform.scale(img,
                                                             (BLOCK_SIZE, BLOCK_SIZE))

        # IMG BOMBERMAN
        img = pygame.image.load(os.path.join(resource_path, "bomberman.png"))
        self.__imgDictionary[PLAYER] = pygame.transform.scale(img,
                                                              (BLOCK_SIZE, BLOCK_SIZE))

        # IMG ENEMY
        img = pygame.image.load(os.path.join(resource_path, "enemy.png"))
        self.__imgDictionary[ENEMY] = pygame.transform.scale(img,
                                                             (BLOCK_SIZE, BLOCK_SIZE))

        # IMG BOMB
        img = pygame.image.load(os.path.join(resource_path, "bomb.png"))
        self.__imgDictionary[BOMB] = pygame.transform.scale(img,
                                                            (BLOCK_SIZE, BLOCK_SIZE))

        # BACKGROUND
        img = pygame.image.load(os.path.join(resource_path, "background.jpg"))
        self.__imgBackground = pygame.transform.scale(img, (SIZE, SIZE))

    def __printOnScreen(self, surface) -> None:

        if gameInstance.getFinish() is None:
            for i in range(gameInstance.getSize()):
                for j in range(gameInstance.getSize()):

                    if gameInstance.getElement(i, j) in self.__imgDictionary.keys():
                        img = self.__imgDictionary[gameInstance.getElement(i, j)]
                        surface.blit(img, (j * BLOCK_SIZE, i * BLOCK_SIZE))
        else:
            self.__gameOver(surface)

    def update(self, surface) -> None:
        self.__printOnScreen(surface)

    def __gameOver(self, surface) -> None:
        surface.blit(self.__imgBackground, (0, 0))
        X = SIZE // 2
        Y = SIZE // 2
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(f"{gameInstance.getFinish()} Win!", True, GREEN, BLUE)
        textRect = text.get_rect()
        textRect.center = (X, Y)
        surface.blit(text, textRect)


class BombThread(Thread, PointType):
    TIME_LIMIT = 4

    def __init__(self, i=None, j=None):
        PointType.__init__(self, i, j, BOMB)
        Thread.__init__(self)
        self.__listPoints = computeNeighbors(i, j)

    def run(self) -> None:
        sleep(BombThread.TIME_LIMIT)  # time to explode bomb

        gameInstance.lock.acquireWriteLock()
        gameInstance.explode(self.__listPoints, self)
        gameInstance.lock.releaseWriteLock()


class Starting(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self) -> None:
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write('\rBUILDING THE WORLD ' + c)
            sys.stdout.flush()
            sleep(0.1)
        sys.stdout.write('\rDone!     ')


# --- AI ---

# this thread build matrix game world
class MatrixBuilder:
    def __init__(self):

        if os.name == 'nt':
            self.__handler = DesktopHandler(
                DLV2DesktopService(os.path.join(resource_path, "../../lib/DLV2.exe")))
        elif os.uname().sysname == 'Darwin':
            self.__handler = DesktopHandler(
                DLV2DesktopService(os.path.join(resource_path, "../../lib/dlv2.mac_7")))
        else:
            self.__handler = DesktopHandler(
                DLV2DesktopService(os.path.join(resource_path, "../../lib/dlv2-linux-64_6")))

        self.__inputProgram = ASPInputProgram()
        self.__inputProgram.add_files_path(os.path.join(resource_path, "map.dlv2"))
        self.__handler.add_program(self.__inputProgram)

    def build(self) -> List[List[int]]:

        global MAP_SIZE
        worldMap = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        try:

            for i in range(MAP_SIZE):  # adding size matrix
                self.__inputProgram.add_program(f"n({i}).")

            for i in range(int(MAP_SIZE / 2)):  # adding numbers of wall
                self.__inputProgram.add_program(f"wallId({i}).")

            self.__inputProgram.add_program(f"minWood({MAP_SIZE}).")
            self.__inputProgram.add_program(f"maxWood({MAP_SIZE * 2}).")

            Starting().start()
            answerSets = self.__handler.start_sync()

            print("~~~~~~~~~~~~~~~~~~~~~~  MATRIX ~~~~~~~~~~~~~~~~~~~~~~")
            if len(answerSets.get_answer_sets()) == 0:
                raise Exception

            for answerSet in answerSets.get_answer_sets():
                print(answerSet)
                for obj in answerSet.get_atoms():
                    if isinstance(obj, InputPointType):
                        worldMap[obj.get_i()][obj.get_j()] = obj.get_t()

            for row in worldMap:
                print(row)

            print("~~~~~~~~~~~~~~~~~~~~~~  END MATRIX ~~~~~~~~~~~~~~~~~~~~~~")

            self.__handler.remove_all()
        except Exception as e:
            MAP_SIZE = 16
            worldMap = [[1, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
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
        finally:
            global done
            done = True
            return worldMap


class DLVSolution:

    def __init__(self):
        self.__countLogs = 0  # count for debug
        self.__dir = None  # log directory for debug
        self.__lastPositionsEnemy = {}  # check all last position of enemy
        self.__bombs = ListBomb()  # list of bomb already placed

        try:
            if os.name == 'nt':
                self.__handler = DesktopHandler(
                    DLV2DesktopService(os.path.join(resource_path, "../../lib/DLV2.exe")))
            elif os.uname().sysname == 'Darwin':
                self.__handler = DesktopHandler(
                    DLV2DesktopService(os.path.join(resource_path, "../../lib/dlv2.mac_7")))
            else:
                self.__handler = DesktopHandler(
                    DLV2DesktopService(os.path.join(resource_path, "../../lib/dlv2-linux-64_6")))
            self.__fixedInputProgram = ASPInputProgram()
            self.__variableInputProgram = None

            self.__fixedInputProgram.add_files_path(os.path.join(resource_path, "enemyRules.dlv2"))
            self.__handler.add_program(self.__fixedInputProgram)

        except Exception as e:
            print(str(e))

    # DEBUG

    def __log_program(self) -> None:
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

    def recallASP(self) -> None:
        try:
            print("RECALL ASP")
            #
            # print(f" ENEMY: {gameInstance.getEnemy()} \n "
            #       f"PLAYER: {gameInstance.getPlayer()}")
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
                    print(f"Distance: {d} --> {distance}")
                    self.__variableInputProgram.add_object_input(d)

            # adding last position
            if len(self.__lastPositionsEnemy) != 0:
                for enemy in self.__lastPositionsEnemy:
                    self.__variableInputProgram.add_program(
                        f"lastPositionEnemy({enemy.get_i()}, {enemy.get_j()}, {self.__lastPositionsEnemy[enemy]}).")

            # adding bombs ai
            for bomb in self.__bombs:
                self.__variableInputProgram.add_object_input(bomb)

            index = self.__handler.add_program(self.__variableInputProgram)
            answerSets = self.__handler.start_sync()

            self.__log_program()
            print("#######################################")
            print(answerSets.get_answer_sets_string())
            for answerSet in answerSets.get_optimal_answer_sets():
                print(answerSet)
                for obj in answerSet.get_atoms():
                    if isinstance(obj, Path):
                        moveEnemyFromPath(obj, self.__lastPositionsEnemy)
                    elif isinstance(obj, InputBomb):
                        addBombEnemy(self.__bombs, obj)
                    elif isinstance(obj, EnemyBomb):
                        gameInstance.plantBomb(obj.get_i(), obj.get_j())
                        bomb = InputBomb(obj.get_i(), obj.get_j())
                        addBombEnemy(self.__bombs, bomb)
                    elif isinstance(obj, BreakBomb):
                        gameInstance.plantBomb(obj.get_i(), obj.get_j())
                        bomb = InputBomb(obj.get_i(), obj.get_j())
                        addBombEnemy(self.__bombs, bomb)
                    elif isinstance(obj, AdjacentPlayerAndEnemy):
                        self.__lastPositionsEnemy.clear()  # clear last enemy position because enemy find player

            print("#######################################")

            self.__handler.remove_program_from_id(index)

        except Exception as e:
            print(str(e))


class DLVThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.dlv = DLVSolution()

    def run(self) -> None:
        while is_running:
            try:
                gameInstance.lock.acquireWriteLock()
                finish = gameInstance.getFinish()
                if finish is not None:
                    break
                self.dlv.recallASP()
            finally:
                gameInstance.lock.releaseWriteLock()
            sleep(0.5)


class ListBomb:
    def __init__(self):
        self.__l = []
        self.__lock = RWLock()

    def append(self, elem: InputBomb):
        self.__lock.acquireWriteLock()
        self.__l.append(elem)
        self.__lock.releaseWriteLock()

    def remove(self, elem: InputBomb):
        self.__lock.acquireWriteLock()
        self.__l.remove(elem)
        self.__lock.releaseWriteLock()

    def __contains__(self, elem: InputBomb):
        try:
            self.__lock.acquireReadLock()
            return elem in self.__l
        except Exception as e:
            self.__lock.acquireReadLock()
            return False
        finally:
            self.__lock.releaseReadLock()

    def __iter__(self):
        try:
            self.__lock.acquireReadLock()
            return iter(self.__l.copy())
        finally:
            self.__lock.releaseReadLock()


class CheckBomb(Thread):

    def __init__(self, listBomb: ListBomb, bomb: InputBomb):
        Thread.__init__(self)
        self.__bombs = listBomb
        self.__bomb = bomb

    def run(self) -> None:
        stop = False
        while not stop:
            gameInstance.lock.acquireReadLock()
            isGrass = gameInstance.getElement(self.__bomb.get_i(), self.__bomb.get_j()) == GRASS

            if isGrass:
                self.__bombs.remove(self.__bomb)
                stop = True

            gameInstance.lock.releaseReadLock()


# === FUNCTIONS === (lower_case names)

ASPMapper.get_instance().register_class(InputPointType)
ASPMapper.get_instance().register_class(Path)
ASPMapper.get_instance().register_class(Distance)
ASPMapper.get_instance().register_class(InputBomb)
ASPMapper.get_instance().register_class(EnemyBomb)
ASPMapper.get_instance().register_class(BreakBomb)
ASPMapper.get_instance().register_class(AdjacentPlayerAndEnemy)


def addBombEnemy(bombs: ListBomb, bomb: InputBomb) -> None:
    if bomb not in bombs:
        bombs.append(bomb)
        CheckBomb(bombs, bomb).start()


def moveEnemyFromPath(path: Path, lastPositionsEnemy: dict) -> None:
    enemyLastPositionTmp = copy.deepcopy(gameInstance.getEnemy())
    if enemyLastPositionTmp not in lastPositionsEnemy:
        lastPositionsEnemy[enemyLastPositionTmp] = 0
    else:
        lastPositionsEnemy[enemyLastPositionTmp] += 1
    gameInstance.moveEnemy(path)


def movePoint(point: Point, directions: int) -> None:
    if directions in MOVEMENTS_MATRIX.keys():
        point.increase_i(MOVEMENTS_MATRIX[directions][Point.I])
        point.increase_j(MOVEMENTS_MATRIX[directions][Point.J])


def getDistanceEP(p1: Point, e1: Point) -> int:
    pI = p1.get_i()
    pJ = p1.get_j()
    eI = e1.get_i()
    eJ = e1.get_j()

    return int(pow(pow(eI - pI, 2) + pow(eJ - pJ, 2), 1 / 2))


def computeNeighbors(i: int, j: int) -> List[Point]:
    listPoints = [Path(i, j) for _ in range(4)]
    movePoint(listPoints[0], LEFT)
    movePoint(listPoints[1], RIGHT)
    movePoint(listPoints[2], UP)
    movePoint(listPoints[3], DOWN)

    return listPoints


def setCharacter(character: Point, coordinate: tuple) -> None:
    character.set_i(coordinate[0])
    character.set_j(coordinate[1])


def collision(i: int, j: int) -> bool:
    try:
        return gameInstance.outBorders(i, j) or gameInstance.getElement(i, j) != GRASS
    except Exception as e:
        return True


def collisionBomb(i: int, j: int) -> bool:
    try:
        return gameInstance.outBorders(i, j) or gameInstance.getElement(i, j) == BLOCK or gameInstance.getElement(i,
                                                                                                                  j) == BOMB
    except Exception as e:
        return True


def move(directions: int, point) -> None:
    oldPoint = copy.deepcopy(point)

    if directions in MOVEMENTS_MATRIX.keys():
        movePoint(point, directions)

    if collision(point.get_i(), point.get_j()):
        point.set_i(oldPoint.get_i())
        point.set_j(oldPoint.get_j())
    else:
        gameInstance.moveOnMap(point, oldPoint)


def plant() -> None:
    i = gameInstance.getPlayer().get_i() + lastMovement[Point.I]
    j = gameInstance.getPlayer().get_j() + lastMovement[Point.J]
    gameInstance.plantBomb(i, j)


# === MAIN === (lower_case names)

# --- (global) variables ---
done: bool = False
is_running: bool = True

buildMatrix = MatrixBuilder()
world = buildMatrix.build()
dlvThread = DLVThread()
gameInstance = Game()

gameInstance.lock.acquireWriteLock()
gameInstance.setMap(world)
gameInstance.lock.releaseWriteLock()

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
                gameInstance.lock.acquireWriteLock()
                player = gameInstance.getPlayer()
                move(direction, player)
                gameInstance.lock.releaseWriteLock()
            elif event.key == pygame.K_SPACE:
                gameInstance.lock.acquireWriteLock()
                plant()
                gameInstance.lock.releaseWriteLock()

    # --- draws ---

    gameInstance.lock.acquireReadLock()
    handler.update(screen)
    gameInstance.lock.releaseReadLock()

    pygame.display.update()

    # --- FPS ---

    clock.tick(25)

# --- the end ---

pygame.quit()
sys.exit(0)
