import os

from application.model.Game import Game


class Settings:
    # GAME
    GRASS = 0
    PLAYER = 1
    ENEMY = 2
    BLOCK = 3
    BOX = 4
    BOMB = 5

    # SCREEN
    SIZE = 800
    BLOCK_SIZE = SIZE // Game.size
    current_path = os.path.dirname(__file__)  # Where your .py file is located
    resource_path = os.path.join(current_path, 'resources')  # The resource folder path
