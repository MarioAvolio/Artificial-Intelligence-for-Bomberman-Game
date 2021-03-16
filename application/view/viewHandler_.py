import os

import pygame

from application.model.game import Game
from application.settings_ import Settings


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class ViewHandler(Singleton):
    def __init__(self):
        Game()
        pygame.init()
        self.__screen = pygame.display.set_mode((Settings.SIZE, Settings.SIZE))

        # set the pygame window name
        pygame.display.set_caption('BomberFriends')

        # change icon
        programIcon = pygame.image.load(os.path.join(Settings.resource_path, "icon.png"))
        pygame.display.set_icon(programIcon)

        # PATH
        terrainPath = os.path.join(Settings.resource_path, "terrain")

        # IMG DICTIONARY
        self.__imgdictionary = {}

        # IMG TERRAIN
        img = pygame.image.load(os.path.join(terrainPath, "block.png"))
        self.__imgdictionary[Settings.BLOCK] = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        img = pygame.image.load(os.path.join(terrainPath, "box.png"))
        self.__imgdictionary[Settings.BOX] = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        img = pygame.image.load(os.path.join(terrainPath, "grass.png"))
        self.__imgdictionary[Settings.GRASS] = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # IMG BOMBERMAN
        img = pygame.image.load(os.path.join(Settings.resource_path, "bomberman.png"))
        self.__imgdictionary[Settings.PLAYER] = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # IMG ENEMY
        img = pygame.image.load(os.path.join(Settings.resource_path, "enemy.png"))
        self.__imgdictionary[Settings.ENEMY] = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # IMG BOMB
        img = pygame.image.load(os.path.join(Settings.resource_path, "bomb.png"))
        self.__imgdictionary[Settings.BOMB] = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))

        # BACKGROUND
        img = pygame.image.load(os.path.join(Settings.resource_path, "background.jpg"))
        self.__imgBackground = pygame.transform.scale(img, (Settings.SIZE, Settings.SIZE))

    def update(self):
        if Game.getInstance().getFinish() is None:
            for i in range(Game.getInstance().getSize()):
                for j in range(Game.getInstance().getSize()):

                    if Game.getInstance().getElement(i, j) in self.__imgdictionary.keys():
                        img = self.__imgdictionary[Game.getInstance().getElement(i, j)]
                        self.__screen.blit(img, (j * Settings.BLOCK_SIZE, i * Settings.BLOCK_SIZE))
        else:
            self.__gameOver()

        pygame.display.update()

    def __gameOver(self):
        # INSIDE OF THE GAME LOOP
        self.__screen.blit(self.__imgBackground, (0, 0))

        # REST OF ITEMS ARE BLIT'D TO SCREEN.
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
        text = font.render(f"{Game.getInstance().getFinish()} Win!", True, green, blue)

        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = (X, Y)

        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        self.__screen.blit(text, textRect)
