class Point:
    I = 0
    J = 1

    def __init__(self, i: int, j: int):
        self.__coordinate = [i, j]  # list

    def getI(self):
        return self.__coordinate[Point.I]

    def getJ(self):
        return self.__coordinate[Point.J]

    def setI(self, i: int):
        self.__coordinate[Point.I] = i

    def setJ(self, j: int):
        self.__coordinate[Point.J] = j

    def move(self, direction: int):
        from application.model.Movements_ import Movements
        if direction in Movements.MOVEMENTS_MATRIX.keys():
            self.__coordinate[Point.I] += Movements.MOVEMENTS_MATRIX[direction][Point.I]
            self.__coordinate[Point.J] += Movements.MOVEMENTS_MATRIX[direction][Point.J]
