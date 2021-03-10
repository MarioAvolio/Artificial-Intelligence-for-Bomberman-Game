import pygame

from application.model.Game_ import Game
from application.model.Movements_ import Movements


class MoveController:
    lastMovement = None
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
                    direction = MoveController.movements[event.key]
                    MoveController.lastMovement = Movements.MOVEMENTS_MATRIX[direction]  # set last movement
                    Movements.move(direction, Game.getInstance().getPlayer())
                elif event.key == pygame.K_SPACE:
                    Movements.plant()

            # elif pygame.KEYUP == event.type:
            #     if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            #         pass

        return True
