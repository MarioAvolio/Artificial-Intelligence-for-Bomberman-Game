import os

import pip

from application.settings_ import Settings


def install_whl(path):
    pip.main(['install', path])


def main():
    install_whl(os.path.join(Settings.resource_path, "../../lib/EmbASP-7.4.0-py2.py3-none-any.whl"))  # EMBASP INSTALLER


if __name__ == '__main__':
    main()
