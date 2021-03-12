import os

import pip
from languages.asp.asp_input_program import ASPInputProgram
from languages.asp.asp_mapper import ASPMapper
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

from application.loop import GameLoop
from application.settings_ import Settings
from application.model.game import Game, Point


def install_whl(path):
    pip.main(['install', path])


def main():
    gl = GameLoop()
    gl.start()


def initializeASP():
    try:

        handler = DesktopHandler(DLV2DesktopService(os.path.join(Settings.resource_path, "../../lib/DLV2.exe")))
        ASPMapper.get_instance().register_class(Point)
        inputProgram = ASPInputProgram()

        # Example facts: point(I, J, ELEMENT_TYPE)
        # input matrix as facts
        size = Game.getInstance().getSize()
        for i in range(size):
            for j in range(size):
                inputProgram.add_program(f"point({i},{j},{Game.getInstance().getElement(i, j)}")

        # input type of elements as facts

        handler.add_program(inputProgram)
        answerSets = handler.start_sync()

        for answerSet in answerSets.get_optimal_answer_sets():
            print(answerSet)

    except Exception as e:
        print("exception")
        print(str(e))


if __name__ == '__main__':
    # install_whl(os.path.join(Settings.resource_path, "../../lib/EmbASP-7.4.0-py2.py3-none-any.whl")) # EMBASP INSTALLER
    # initializeASP()
    main()
