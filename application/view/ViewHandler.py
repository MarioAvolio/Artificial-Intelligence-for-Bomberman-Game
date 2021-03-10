import os

import pygame

from application.Settings_ import Settings
from application.model.Game_ import Game


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class ViewHandler(Singleton):
    def __init__(self):
        pygame.init()
        self.__screen = pygame.display.set_mode((Settings.SIZE, Settings.SIZE))

        # set the pygame window name
        pygame.display.set_caption('BomberFriends')

        # change icon
        programIcon = pygame.image.load(os.path.join(Settings.resource_path, "icon.png"))
        pygame.display.set_icon(programIcon)

        # PATH
        terrainPath = os.path.join(Settings.resource_path, "terrain")

        # IMG TERRAIN
        img = pygame.image.load(os.path.join(terrainPath, "block.png"))
        self.__imgBlock = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))
        img = pygame.image.load(os.path.join(terrainPath, "box.png"))
        self.__imgBox = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))
        img = pygame.image.load(os.path.join(terrainPath, "grass.png"))
        self.__imgGrass = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # IMG BOMBERMAN
        img = pygame.image.load(os.path.join(Settings.resource_path, "bomberman.png"))
        self.__imgBomberman = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # IMG ENEMY
        img = pygame.image.load(os.path.join(Settings.resource_path, "enemy.png"))
        self.__imgEnemy = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # IMG BOMB
        img = pygame.image.load(os.path.join(Settings.resource_path, "bomb.png"))
        self.__imgBomb = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # BACKGROUND
        self.__imgBackground = pygame.image.load(os.path.join(Settings.resource_path, "background.png"))

    def update(self):
        if Game.finish is None:
            for i in range(Game.getInstance().getSize()):
                for j in range(Game.getInstance().getSize()):

                    img = None
                    if Game.getInstance().getElement(i, j) == Settings.BLOCK:
                        img = self.__imgBlock
                    elif Game.getInstance().getElement(i, j) == Settings.BOX:
                        img = self.__imgBox
                    elif Game.getInstance().getElement(i, j) == Settings.PLAYER:
                        img = self.__imgBomberman
                    elif Game.getInstance().getElement(i, j) == Settings.ENEMY:
                        img = self.__imgEnemy
                    elif Game.getInstance().getElement(i, j) == Settings.GRASS:
                        img = self.__imgGrass
                    elif Game.getInstance().getElement(i, j) == Settings.BOMB:
                        img = self.__imgBomb

                    if img is not None:
                        self.__screen.blit(img, (j * Settings.BLOCK_SIZE, i * Settings.BLOCK_SIZE))
        else:
            self.__gameOver()

        pygame.display.update()

    def __gameOver(self):
        # define the RGB value for white,
        #  green, blue colour .
        white = (255, 255, 255)
        green = (0, 255, 0)
        blue = (0, 0, 128)

        # assigning values to X and Y variable
        X = Settings.SIZE // 2
        Y = Settings.SIZE // 2

        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        font = pygame.font.Font('freesansbold.ttf', 32)

        # create a text suface object,
        # on which text is drawn on it.
        text = font.render(f"{Game.finish} Win!", True, green, blue)

        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = (X, Y)

        # completely fill the surface object
        # with white color
        self.__screen.fill(white)

        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        self.__screen.blit(text, textRect)
