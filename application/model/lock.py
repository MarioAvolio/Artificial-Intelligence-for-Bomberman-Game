from threading import RLock, Condition

#
# function of synchronized print
#
pLock = RLock()


def prints(s):
    pLock.acquire()
    print(s, flush=True)
    pLock.release()


class RWLockWithoutStarvation:
    def __init__(self):
        self._numberOfReaders = 0
        self._thereIsAWriter = False
        self._lock = RLock()
        self._condition = Condition(self._lock)

    def acquireReadLock(self):
        self._lock.acquire()
        while self._thereIsAWriter:
            self._condition.wait()
        self._numberOfReaders += 1
        self._lock.release()

    def releaseReadLock(self):
        self._lock.acquire()
        self._numberOfReaders -= 1
        if self._numberOfReaders == 0:
            self._condition.notify()
        self._lock.release()

    def acquireWriteLock(self):
        self._lock.acquire()
        while self._numberOfReaders > 0 or self._thereIsAWriter:
            self._condition.wait()
        self._thereIsAWriter = True
        self._lock.release()

    def releaseWriteLock(self):
        self._lock.acquire()
        self._thereIsAWriter = False
        self._condition.notify_all()
        self._lock.release()


class RWLock(RWLockWithoutStarvation):
    LIMIT = 5

    def __init__(self):
        super().__init__()
        self.__numberOfWritersInWaiting = 0
        self.__numberOfIterationsWithoutWriters = 0

    def acquireReadLock(self):
        self._lock.acquire()
        # print(f"acquireReadLock {Thread.__name__}")
        while self._thereIsAWriter or \
                (self.__numberOfWritersInWaiting > 0 and self.__numberOfIterationsWithoutWriters > self.LIMIT):
            self._condition.wait()
        self._numberOfReaders += 1
        if self.__numberOfWritersInWaiting > 0:
            self.__numberOfIterationsWithoutWriters += 1
        self._lock.release()

    def releaseReadLock(self):
        self._lock.acquire()
        # print(f"releaseReadLock {Thread.__name__}")
        self._numberOfReaders -= 1
        if self._numberOfReaders == 0:
            self._condition.notify_all()
        self._lock.release()

    def acquireWriteLock(self):
        self._lock.acquire()
        # print(f"acquireWriteLock {Thread.__name__}")
        self.__numberOfWritersInWaiting += 1
        while self._numberOfReaders > 0 or self._thereIsAWriter:
            self._condition.wait()
        self._thereIsAWriter = True
        self.__numberOfWritersInWaiting -= 1
        self.__numberOfIterationsWithoutWriters = 0
        self._lock.release()
