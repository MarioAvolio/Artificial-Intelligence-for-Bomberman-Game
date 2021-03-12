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
    initializeASP()


def initializeASP():
    try:

        handler = DesktopHandler(DLV2DesktopService(os.path.join(Settings.resource_path, "../../lib/DLV2.exe")))
        ASPMapper.get_instance().register_class(Point)
        fixedInputProgram = ASPInputProgram()  # rules
        variableInputProgram = ASPInputProgram()  # map

        fixedInputProgram.add_files_path(os.path.join(Settings.resource_path, "rules.dlv2"))
        for elem in range(6):
            fixedInputProgram.add_program(f"elem({elem}).")

        # Example facts: point(I, J, ELEMENT_TYPE)
        # input matrix as facts
        size = Game.getInstance().getSize()
        for i in range(size):
            for j in range(size):
                typeNumber = Game.getInstance().getElement(i, j)
                variableInputProgram.add_program(f"cell({i},{j},{typeNumber}).")
                print(f"cell({i},{j},{typeNumber}).", end=' ')

        print()

        variableInputProgram.clear_all()  # clear at each call
        handler.add_program(fixedInputProgram)
        handler.add_program(variableInputProgram)
        answerSets = handler.start_sync()

        for answerSet in answerSets.get_optimal_answer_sets():
            print(answerSet)

    except Exception as e:
        print("exception")
        print(str(e))


if __name__ == '__main__':
    # install_whl(os.path.join(Settings.resource_path, "../../lib/EmbASP-7.4.0-py2.py3-none-any.whl")) # EMBASP INSTALLER
    main()
