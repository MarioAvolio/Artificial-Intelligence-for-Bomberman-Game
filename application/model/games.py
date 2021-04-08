import copy
import datetime
import itertools
import os
import sys
from threading import Thread, RLock
from time import sleep

import pygame
# === CONSTANS === (UPPER_CASE names)
from languages.asp.asp_input_program import ASPInputProgram
from languages.asp.asp_mapper import ASPMapper
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

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

        self.__size = len(self.__map)
        global BLOCK_SIZE
        BLOCK_SIZE = SIZE // self.__size
        self.lock = RLock()
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
        # print(f"muovo il nemico in {point} dalla precedente posizione {self.__enemy}")
        self.moveOnMap(point, self.__enemy)
        self.__enemy.set_j(point.get_j())
        self.__enemy.set_i(point.get_i())

    def explode(self, listPoints: list[Point], coordinateBomb: Point):
        if self.getFinish() is not None:
            return

        for point in listPoints:  # adjacent point
            if not self.outBorders(point.get_i(), point.get_j()):
                if self.getElement(point.get_i(), point.get_j()) == ENEMY:

                    # debug
                    print(coordinateBomb)
                    for point2 in listPoints:
                        print(point2)

                    for row in self.__map:
                        print(row)

                    self.__finish = "Player"  # player win
                elif self.getElement(point.get_i(), point.get_j()) == PLAYER:

                    # debug
                    print(coordinateBomb)
                    for point2 in listPoints:
                        print(point2)

                    for row in self.__map:
                        print(row)

                    self.__finish = "Enemy"  # enemy win
                elif not collisionBomb(point.get_i(), point.get_j()):
                    self.__writeElement(point.get_i(), point.get_j(), GRASS)

            # remove bomb
        self.__writeElement(coordinateBomb.get_i(), coordinateBomb.get_j(), GRASS)

    # SETTER
    def __writeElement(self, i: int, j: int, elem):
        self.__map[i][j] = elem

    def setMap(self, w: list[list[int]]):
        self.__map = w
        self.__size = len(self.__map)
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
        except:
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

    def __printOnScreen(self, surface) -> None:
        gameInstance.lock.acquire()

        if gameInstance.getFinish() is None:
            for i in range(gameInstance.getSize()):
                for j in range(gameInstance.getSize()):

                    if gameInstance.getElement(i, j) in self.__imgdictionary.keys():
                        img = self.__imgdictionary[gameInstance.getElement(i, j)]
                        surface.blit(img, (j * BLOCK_SIZE, i * BLOCK_SIZE))
        else:
            self.__gameOver(surface)

        pygame.display.update()

        gameInstance.lock.release()

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
    TIME_LIMIT = 3

    def __init__(self, i=None, j=None):
        PointType.__init__(self, i, j, BOMB)
        Thread.__init__(self)
        self.__listPoints = computeNeighbors(i, j)

    def run(self) -> None:
        sleep(BombThread.TIME_LIMIT)  # time to explode bomb

        gameInstance.lock.acquire()
        gameInstance.explode(self.__listPoints, self)
        gameInstance.lock.release()


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
        self.__handler = DesktopHandler(
            DLV2DesktopService(os.path.join(resource_path, "../../lib/DLV2.exe")))
        self.__inputProgram = ASPInputProgram()
        self.__inputProgram.add_files_path(os.path.join(resource_path, "map.dlv2"))
        self.__handler.add_program(self.__inputProgram)

    def build(self) -> list[list[int]]:

        global done
        done = False
        Starting().start()
        answerSets = self.__handler.start_sync()
        done = True
        worldMap = [[0 for x in range(MAP_SIZE)] for y in range(MAP_SIZE)]

        print("~~~~~~~~~~~~~~~~~~~~~~  MATRIX ~~~~~~~~~~~~~~~~~~~~~~")
        # print(answerSets.get_answer_sets_string())
        for answerSet in answerSets.get_answer_sets():
            print(answerSet)
            for obj in answerSet.get_atoms():
                if isinstance(obj, InputPointType):
                    worldMap[obj.get_i()][obj.get_j()] = obj.get_t()

        for row in worldMap:
            print(row)

        print("~~~~~~~~~~~~~~~~~~~~~~  END MATRIX ~~~~~~~~~~~~~~~~~~~~~~")

        self.__handler.remove_all()
        return worldMap


class DLVSolution:

    def __init__(self):
        self.__countLogs = 0  # count for debug
        self.__dir = None  # log directory for debug
        self.__lastPositionsEnemy = {}  # check all last position of enemy
        self.__bombs = []  # list of bomb already placed

        try:
            self.__handler = DesktopHandler(
                DLV2DesktopService(os.path.join(resource_path, "../../lib/DLV2.exe")))

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
        gameInstance.lock.acquire()
        try:

            print(f" ENEMY: {gameInstance.getEnemy()} \n "
                  f"PLAYER: {gameInstance.getPlayer()}")
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
                self.__variableInputProgram.add_object_input(bomb)

            index = self.__handler.add_program(self.__variableInputProgram)
            answerSets = self.__handler.start_sync()

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
                        addBombEnemy(self.__bombs, obj)
                    elif isinstance(obj, BreakBomb):
                        gameInstance.plantBomb(obj.get_i(), obj.get_j())
                        addBombEnemy(self.__bombs, obj)
                    elif isinstance(obj, AdjacentPlayerAndEnemy):
                        self.__lastPositionsEnemy.clear()  # clear last enemy position because enemy find player

            print("#######################################")

            self.__log_program()
            self.__handler.remove_program_from_id(index)

        except Exception as e:
            print(str(e))
        gameInstance.lock.release()


class DLVThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.dlv = DLVSolution()

    def run(self) -> None:
        while is_running:
            gameInstance.lock.acquire()
            finish = gameInstance.getFinish()
            gameInstance.lock.release()
            if finish is not None:
                break
            self.dlv.recallASP()
            sleep(1)


class CheckBomb(Thread):

    def __init__(self, listBomb=None, bomb=None):
        Thread.__init__(self)
        self.__bombs = listBomb
        self.__bomb = bomb

    def run(self) -> None:
        stop = False
        while not stop:
            gameInstance.lock.acquire()
            isGrass = gameInstance.getElement(self.__bomb.get_i(), self.__bomb.get_j()) == GRASS
            gameInstance.lock.release()
            if isGrass:
                self.__bombs.remove(self.__bomb)
                stop = True


# === FUNCTIONS === (lower_case names)

ASPMapper.get_instance().register_class(InputPointType)
ASPMapper.get_instance().register_class(Path)
ASPMapper.get_instance().register_class(Distance)
ASPMapper.get_instance().register_class(InputBomb)
ASPMapper.get_instance().register_class(EnemyBomb)
ASPMapper.get_instance().register_class(BreakBomb)
ASPMapper.get_instance().register_class(AdjacentPlayerAndEnemy)


def addBombEnemy(bombs: list[Point], bomb: Point) -> None:
    if bomb not in bombs:
        bombs.append(bomb)
        CheckBomb(bombs, bomb).start()


def moveEnemyFromPath(path: Path, lastPositionsEnemy: dict) -> None:
    gameInstance.lock.acquire()
    enemyLastPositionTmp = copy.deepcopy(gameInstance.getEnemy())
    if enemyLastPositionTmp not in lastPositionsEnemy:
        lastPositionsEnemy[enemyLastPositionTmp] = 0
    else:
        lastPositionsEnemy[enemyLastPositionTmp] += 1
    gameInstance.moveEnemy(path)
    gameInstance.lock.release()


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


def computeNeighbors(i: int, j: int) -> list[Point]:
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
    gameInstance.lock.acquire()
    try:
        return gameInstance.outBorders(i, j) or gameInstance.getElement(i, j) != GRASS
    finally:
        gameInstance.lock.release()


def collisionBomb(i: int, j: int) -> bool:
    gameInstance.lock.acquire()
    try:
        return gameInstance.outBorders(i, j) or gameInstance.getElement(i, j) == BLOCK or gameInstance.getElement(i,
                                                                                                                  j) == BOMB
    finally:
        gameInstance.lock.release()


def move(directions: int, point) -> None:
    gameInstance.lock.acquire()
    oldPoint = copy.deepcopy(point)

    if directions in MOVEMENTS_MATRIX.keys():
        movePoint(point, directions)

    if collision(point.get_i(), point.get_j()):
        point.set_i(oldPoint.get_i())
        point.set_j(oldPoint.get_j())
    else:
        gameInstance.moveOnMap(point, oldPoint)
    gameInstance.lock.release()


def plant() -> None:
    gameInstance.lock.acquire()
    i = gameInstance.getPlayer().get_i() + lastMovement[Point.I]
    j = gameInstance.getPlayer().get_j() + lastMovement[Point.J]
    gameInstance.plantBomb(i, j)
    gameInstance.lock.release()


# === MAIN === (lower_case names)

# --- (global) variables ---
buildMatrix = MatrixBuilder()
world = buildMatrix.build()
dlvThread = DLVThread()
gameInstance = Game()
done: bool = False
is_running: bool = True

gameInstance.lock.acquire()
gameInstance.setMap(world)
gameInstance.lock.release()

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
                gameInstance.lock.acquire()
                player = gameInstance.getPlayer()
                gameInstance.lock.release()
                move(direction, player)
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
