class Point:
    def __init__(self, i: int, j: int):
        self.__i = i
        self.__j = j

    def getI(self):
        return self.__i

    def getJ(self):
        return self.__j

    def setI(self, i: int):
        self.__i = i

    def setJ(self, j: int):
        self.__j = j

    def moveUp(self):
        self.__i -= 1

    def moveDown(self):
        self.__i += 1

    def moveLeft(self):
        self.__j -= 1

    def moveRight(self):
        self.__j += 1

    def __str__(self):
        return str(self.__i) + ", " + str(self.__j)
