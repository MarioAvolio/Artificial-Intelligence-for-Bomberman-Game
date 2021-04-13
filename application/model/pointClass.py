from languages.predicate import Predicate


class Point:
    I = 0
    J = 1

    def __init__(self, i=None, j=None):
        self._coordinate = [i, j]  # list

    def get_i(self):
        return self._coordinate[Point.I]

    def get_j(self):
        return self._coordinate[Point.J]

    def set_i(self, i: int):
        self._coordinate[Point.I] = i

    def set_j(self, j: int):
        self._coordinate[Point.J] = j

    def increase_i(self, increase: int):
        self._coordinate[Point.I] += increase

    def increase_j(self, increase: int):
        self._coordinate[Point.J] += increase

    def __str__(self):
        return f"Point [{self._coordinate[Point.I]}, {self._coordinate[Point.J]}]."

    def __key(self):
        return self.get_i(), self.get_j()

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.__key() == other.__key()
        return NotImplemented

    def __hash__(self):
        return hash(self.__key())


class PointType(Point):

    def __init__(self, i=None, j=None, t=None):
        Point.__init__(self, i, j)
        self.__t = t

    def get_t(self):
        return self.__t

    def set_t(self, t: int):
        self.__t = t


class InputPointType(Predicate, PointType):
    predicate_name = "point"

    def __init__(self, i=None, j=None, t=None):
        Predicate.__init__(self, [("i", int), ("j", int), ("t", int)])
        PointType.__init__(self, i, j, t)


class EnemyBomb(Predicate, Point):
    predicate_name = "enemyBomb"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class BreakBomb(Predicate, Point):
    predicate_name = "breakBomb"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class InputBomb(Predicate, Point):
    predicate_name = "bomb"

    def __init__(self, i=None, j=None):
        Point.__init__(self, i, j)
        Predicate.__init__(self, [("i", int), ("j", int)])


class Path(Predicate, Point):
    predicate_name = "path"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class AdjacentPlayerAndEnemy(Predicate, Point):
    predicate_name = "adjacentPlayerAndEnemy"

    def __init__(self, i=None, j=None):
        Predicate.__init__(self, [("i", int), ("j", int)])
        Point.__init__(self, i, j)


class Distance(Predicate, Point):
    predicate_name = "distance"

    def __init__(self, i=None, j=None, d=None):
        Predicate.__init__(self, [("i", int), ("j", int), ("d", int)])
        Point.__init__(self, i, j)
        self.d = d

    def get_d(self):
        return self.d

    def set_d(self, d: int):
        self.d = d
