import pygame

from application.model.Game import Game
from application.model.Movements import Movements


class MoveController:
    movements = {
        pygame.K_LEFT: Movements.LEFT,
        pygame.K_RIGHT: Movements.RIGHT,
        pygame.K_DOWN: Movements.DOWN,
        pygame.K_UP: Movements.UP
    }

    def __init__(self):
        pass

    @staticmethod
    def update() -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # controller
            if event.type == pygame.KEYDOWN:
                if event.key in MoveController.movements:
                    Movements.move(MoveController.movements[event.key], Game.getInstance().getPlayer())
            # elif pygame.KEYUP == event.type:
            #     if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            #         pass

        return True
