import pip

from application.loop import GameLoop


def install_whl(path):
    pip.main(['install', path])


def main():
    gl = GameLoop()
    gl.start()


if __name__ == '__main__':
    # install_whl(os.path.join(Settings.resource_path, "../../lib/EmbASP-7.4.0-py2.py3-none-any.whl")) # EMBASP INSTALLER
    main()
