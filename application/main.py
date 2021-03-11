import os

import pip
from languages.asp.asp_input_program import ASPInputProgram
from languages.asp.asp_mapper import ASPMapper
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService

from application.GameLoop import GameLoop
from application.Settings_ import Settings
from application.model.Point_ import Point


def install_whl(path):
    pip.main(['install', path])


def main():
    gl = GameLoop()
    gl.start()
    handler = DesktopHandler(DLV2DesktopService(os.path.join(Settings.resource_path, "DLV2.exe")))


def initializeASP():
    try:

        handler = DesktopHandler(DLV2DesktopService(os.path.join(Settings.resource_path, "DLV2.exe")))
        ASPMapper.get_instance().register_class(Point)
        inputProgram = ASPInputProgram()

        rules = "point(Y,X) :- point(X,Y)."

        inputProgram.add_program(rules)
        inputProgram.add_program("point(1,2).")
        handler.add_program(inputProgram)
        answerSets = handler.start_sync()

        for answerSet in answerSets.get_optimal_answer_sets():
            print(answerSet)

            for obj in answerSet.get_atoms():

                if isinstance(obj, Point):
                    print(answerSet)

    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    # install_whl(os.path.join(Settings.resource_path, "../../lib/EmbASP-7.4.0-py2.py3-none-any.whl")) # EMBASP INSTALLER
    # main()
    initializeASP()
