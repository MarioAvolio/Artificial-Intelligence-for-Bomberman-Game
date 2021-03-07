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
        # add background img
        # self.__screen.blit(self.__imgBackground, (0, 0))
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

        pygame.display.update()
