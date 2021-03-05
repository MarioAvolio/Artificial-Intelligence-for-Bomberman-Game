import os


class Settings:
    # GAME
    NONE = 0
    PLAYER = 1
    ENEMY = 2
    BLOCK1 = 3

    # SCREEN
    SIZE = 800
    BLOCK_SIZE = None
    current_path = os.path.dirname(__file__)  # Where your .py file is located
    resource_path = os.path.join(current_path, 'resources')  # The resource folder path
