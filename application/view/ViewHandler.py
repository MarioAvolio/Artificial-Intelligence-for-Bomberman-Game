import os

import pygame

from application.Settings import Settings
from application.model.Game import Game, Singleton


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

        # BACKGROUND
        self.__imgBackground = pygame.image.load(os.path.join(Settings.resource_path, "background.png"))

    def update(self):
        # add background img
        # self.__screen.blit(self.__imgBackground, (0, 0))
        for i in range(Game().size):
            for j in range(Game().size):

                img = None
                if Game.map[i][j] == Settings.BLOCK:
                    img = self.__imgBlock
                elif Game.map[i][j] == Settings.BOX:
                    img = self.__imgBox
                elif Game.map[i][j] == Settings.PLAYER:
                    img = self.__imgBomberman
                elif Game.map[i][j] == Settings.ENEMY:
                    img = self.__imgEnemy
                elif Game.map[i][j] == Settings.GRASS:
                    img = self.__imgGrass

                if img is not None:
                    self.__screen.blit(img, (j * Settings.BLOCK_SIZE, i * Settings.BLOCK_SIZE))

        pygame.display.update()
