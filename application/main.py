import os

import pip

from application.GameLoop import GameLoop
from application.Settings_ import Settings


def install_whl(path):
    pip.main(['install', path])


def main():
    gl = GameLoop()
    gl.start()


if __name__ == '__main__':
    install_whl(os.path.join(Settings.resource_path, "EmbASP-7.4.0-py2.py3-none-any.whl"))
    main()
