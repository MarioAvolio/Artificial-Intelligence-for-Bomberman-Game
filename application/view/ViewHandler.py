import os

import pygame

from application.Settings import Settings
from application.model.Game import Game

game = Game()


class ViewHandler:
    def __init__(self):
        pygame.init()
        self.__screen = pygame.display.set_mode((Settings.SIZE, Settings.SIZE))

    def update(self) -> bool:

        img = pygame.image.load(os.path.join(Settings.resource_path, "battleship.png"))
        img = pygame.transform.scale(img, (Settings.BLOCK_SIZE, Settings.BLOCK_SIZE))
        self.__screen.blit(img, (Settings.SIZE / 2, Settings.SIZE / 2))  # resize

        while 1:
            maps = game.getMap()
            self.__screen.fill(0)
            for i in range(game.size):
                for j in range(game.size):
                    if maps[i][j] == Settings.BLOCK1:
                        self.__screen.blit(img, (0, 0))

            pygame.display.flip()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
