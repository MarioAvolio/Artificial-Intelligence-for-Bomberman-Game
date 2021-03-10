from threading import Thread
from time import sleep

import pygame

from application.controller.MoveController import MoveController
from application.view.ViewHandler import ViewHandler


class GameLoop(Thread):
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        vh = ViewHandler()
        while MoveController.update():
            vh.update()
            sleep(0.1)

        # deactivates the pygame library
        pygame.quit()

        # quit the program.
        quit()
