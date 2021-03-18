import copy
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

BLOCK_SIZE = 50


# === CLASSES === (CamelCase names)

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
            self.__player = Point(0, 0)
            self.__enemy = Point(7, 9)
            self.__map = [[1, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [4, 0, 0, 0, 0, 0, 4, 4, 0, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 4, 0, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [4, 0, 0, 0, 3, 0, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 2, 0, 0, 3, 3, 3, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
            self.__size = len(self.__map)
            global BLOCK_SIZE
            BLOCK_SIZE = SIZE // self.__size
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

            if collision(i, j):
                return

            self.__writeElement(i, j, BOMB)
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


class Point(Predicate):
    predicate_name = "point"
    I = 0
    J = 1

    def __init__(self, i=None, j=None, t=None):
        Predicate.__init__(self, [("i", int), ("j", int), ("type", int)])
        self.__coordinate = [i, j]  # list
        self.__type = t

    def get_i(self):
        return self.__coordinate[Point.I]

    def get_j(self):
        return self.__coordinate[Point.J]

    def get_type(self):
        return self.__type

    def set_type(self, t: int):
        self.__type = t

    def set_i(self, i: int):
        self.__coordinate[Point.I] = i

    def set_j(self, j: int):
        self.__coordinate[Point.J] = j

    def move(self, direction: int):
        if direction in MOVEMENTS_MATRIX.keys():
            self.__coordinate[Point.I] += MOVEMENTS_MATRIX[direction][Point.I]
            self.__coordinate[Point.J] += MOVEMENTS_MATRIX[direction][Point.J]

    def __str__(self):
        return f"Point({self.__coordinate[Point.I]}, {self.__coordinate[Point.J]}) \n"


class Bomb(Thread, Point):
    def __init__(self, i: int, j: int):
        Thread.__init__(self)
        Point.__init__(self, i, j)
        self.__listPoints = computeNeighbors(i, j)

    def run(self) -> None:
        sleep(2)  # time to explode bomb
        Game.getInstance().explode(self.__listPoints, self)


class HandlerView:
    def __init__(self):
        Game.getInstance()

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
        if Game.getInstance().getFinish() is None:
            for i in range(Game.getInstance().getSize()):
                for j in range(Game.getInstance().getSize()):

                    if Game.getInstance().getElement(i, j) in self.__imgdictionary.keys():
                        img = self.__imgdictionary[Game.getInstance().getElement(i, j)]
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
        text = font.render(f"{Game.getInstance().getFinish()} Win!", True, GREEN, BLUE)
        textRect = text.get_rect()
        textRect.center = (X, Y)
        surface.blit(text, textRect)


class DLVSolution:

    def __init__(self):
        try:
            self.__handler = DesktopHandler(
                DLV2DesktopService(os.path.join(resource_path, "../../lib/DLV2.exe")))
            ASPMapper.get_instance().register_class(Point)
            self.__fixedInputProgram = ASPInputProgram()

            self.__fixedInputProgram.add_files_path(os.path.join(resource_path, "rules.dlv2"))
            for elem in range(6):
                self.__fixedInputProgram.add_program(f"elem({elem}).")
            self.__handler.add_program(self.__fixedInputProgram)

        except Exception as e:
            print(str(e))

    def recallASP(self):
        try:
            size = Game.getInstance().getSize()
            variableInputProgram = ASPInputProgram()

            # input matrix as facts
            for i in range(size):
                for j in range(size):
                    typeNumber = Game.getInstance().getElement(i, j)
                    variableInputProgram.add_program(f"cell({i},{j},{typeNumber}).")  # cell(I, J, ELEMENT_TYPE)

            # compute neighbors values
            e = Game.getInstance().getEnemy()
            p = Game.getInstance().getPlayer()

            listAdjacent = computeNeighbors(e.get_i(), e.get_j())
            for adjacent in listAdjacent:
                if not Game.getInstance().outBorders(adjacent.get_i(), adjacent.get_j()):
                    variableInputProgram.add_program(
                        f"distance({adjacent.get_i()}, {adjacent.get_j()}, {getDistanceEP(adjacent, p)}).")

            index = self.__handler.add_program(variableInputProgram)
            answerSets = self.__handler.start_sync()

            # Problem: index out range
            print("#######################################")
            for answerSet in answerSets.get_optimal_answer_sets():
                print(answerSet)
                a = answerSet.get_atoms()
                print(a)
                for obj in answerSet.get_atoms():
                    if isinstance(obj, Point):
                        print(obj)
                print("#######################################")

            self.__handler.remove_program_from_id(index)

        except Exception as e:
            print(str(e))


class DLVThread(Thread):
    def __init__(self):
        super().__init__()
        self.__dlv = DLVSolution()

    def run(self):
        while True:
            self.__dlv.recallASP()
            sleep(2)


'''
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center
        self.move_x = 0
        self.move_y = 0
        self.gravity = 1
        self.jump = 0
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    def update(self):
        self.rect.x += self.move_x
        self.rect.y += self.move_y
        self.jump -= self.gravity
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.move_x -= 10
            elif event.key == pygame.K_RIGHT:
                self.move_x += 10
            elif event.key == pygame.K_UP:
                self.move_y -= 10
            elif event.key == pygame.K_DOWN:
                self.move_y += 10
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
               self.move_x += 10
            elif event.key == pygame.K_RIGHT:
                self.move_x -= 10
            elif event.key == pygame.K_UP:
                self.move_y += 10
            elif event.key == pygame.K_DOWN:
                self.move_y -= 10
'''


# === FUNCTIONS === (lower_case names)

def getDistanceEP(p1: Point, e1: Point):
    PI = p1.get_i()
    PJ = p1.get_j()
    EI = e1.get_i()
    EJ = e1.get_j()

    return int(pow(pow(EI - PI, 2) + pow(EJ - PJ, 2), 1 / 2))


def computeNeighbors(i: int, j: int):
    listPoints = [Point(i, j) for _ in range(4)]
    listPoints[0].move(LEFT)
    listPoints[1].move(RIGHT)
    listPoints[2].move(UP)
    listPoints[3].move(DOWN)

    return listPoints


def collision(i: int, j: int) -> bool:
    return Game.getInstance().outBorders(i, j) or Game.getInstance().getElement(i, j) != GRASS


def collisionBomb(i: int, j: int) -> bool:
    return Game.getInstance().outBorders(i, j) or Game.getInstance().getElement(i, j) == BLOCK


def move(direction: int, point):
    oldPoint = copy.deepcopy(point)

    if direction in MOVEMENTS_MATRIX.keys():
        point.move(direction)

    if collision(point.get_i(), point.get_j()):
        point.set_i(oldPoint.get_i())
        point.set_j(oldPoint.get_j())
    else:
        Game.getInstance().moveOnMap(point, oldPoint)


def plant():
    i = Game.getInstance().getPlayer().get_i() + lastMovement[Point.I]
    j = Game.getInstance().getPlayer().get_j() + lastMovement[Point.J]
    Game.getInstance().plantBomb(i, j)


# === MAIN === (lower_case names)

# --- (global) variables ---

# --- init ---

pygame.init()

screen = pygame.display.set_mode((SIZE, SIZE))
screen_rect = screen.get_rect()
pygame.display.set_caption('BomberFriends')
programIcon = pygame.image.load(os.path.join(resource_path, "icon.png"))
pygame.display.set_icon(programIcon)

# --- objects ---

handler = HandlerView()
DLVThread().start()

# --- mainloop ---

clock = pygame.time.Clock()
IS_RUNNING = True

while IS_RUNNING:

    # --- events ---

    for event in pygame.event.get():

        # --- global events ---

        if event.type == pygame.QUIT:
            IS_RUNNING = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                IS_RUNNING = False
            if event.key in movements:
                direction = movements[event.key]
                lastMovement = MOVEMENTS_MATRIX[direction]  # set last movement
                move(direction, Game.getInstance().getPlayer())
            elif event.key == pygame.K_SPACE:
                plant()
                pass

        # --- objects events ---

        '''
        player.handle_event(event)
        '''

    # --- updates ---

    '''
    player.update()
    '''

    # --- draws ---

    screen.fill(BLACK)

    '''
    player.draw(screen)
    '''
    handler.update(screen)

    pygame.display.update()

    # --- FPS ---

    clock.tick(25)

# --- the end ---

pygame.quit()
