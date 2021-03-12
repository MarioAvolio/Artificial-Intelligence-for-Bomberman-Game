from threading import Thread
from time import sleep

from application.controller.controllerGame import MoveController
from application.view.viewHandler_ import ViewHandler


class GameLoop(Thread):
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        vh = ViewHandler()
        while MoveController.update():
            vh.update()
            sleep(0.1)

        # # deactivates the pygame library
        # pygame.quit()
        #
        # # quit the program.
        # quit()
