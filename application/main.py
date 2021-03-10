import os

import pip
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

from application.GameLoop import GameLoop
from application.Settings_ import Settings


def install_whl(path):
    pip.main(['install', path])


def main():
    gl = GameLoop()
    gl.start()
    handler = DesktopHandler(DLV2DesktopService(os.path.join(Settings.resource_path, "DLV2.exe")))


if __name__ == '__main__':
    # install_whl(os.path.join(Settings.resource_path, "EmbASP-7.4.0-py2.py3-none-any.whl")) # EMBASP INSTALLER
    main()
