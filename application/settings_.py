import os


class Settings:
    # GAME
    GRASS = 0
    PLAYER = 1
    ENEMY = 2
    BLOCK = 3
    BOX = 4
    BOMB = 5

    # mapString = {
    #     GRASS: "grass",
    #     PLAYER: "player",
    #     ENEMY: "enemy",
    #     BLOCK: "block",
    #     BOX: "box",
    #     BOMB: "bomb"
    # }

    # SCREEN
    SIZE = 800
    BLOCK_SIZE = None
    current_path = os.path.dirname(__file__)  # Where your .py file is located
    resource_path = os.path.join(current_path, 'resources')  # The resource folder path
