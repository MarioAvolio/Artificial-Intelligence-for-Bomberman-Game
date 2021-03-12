import pygame

from application.model import dependance
from application.model.game import Game, Movements


class MoveController:

    def __init__(self):
        pass

    @staticmethod
    def update() -> bool:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            # controller
            if event.type == pygame.KEYDOWN:
                if event.key in dependance.movements:
                    direction = dependance.movements[event.key]
                    dependance.lastMovement = dependance.MOVEMENTS_MATRIX[direction]  # set last movement
                    Movements.move(direction, Game.getInstance().getPlayer())
                elif event.key == pygame.K_SPACE:
                    Movements.plant()

            # elif pygame.KEYUP == event.type:
            #     if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            #         pass

        return True