import pygame


class MoveController:
    def __init__(self):
        pass

    @staticmethod
    def update() -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        return True
