from threading import RLock, Condition


class RWLockWithoutStarvation:
    def __init__(self):
        self.numberOfReaders = 0
        self.thereIsAWriter = False
        self.lock = RLock()
        self.condition = Condition(self.lock)

    def acquireReadLock(self):
        self.lock.acquire()
        while self.thereIsAWriter:
            self.condition.wait()
        self.numberOfReaders += 1
        self.lock.release()

    def releaseReadLock(self):
        self.lock.acquire()
        self.numberOfReaders -= 1
        if self.numberOfReaders == 0:
            self.condition.notify()
        self.lock.release()

    def acquireWriteLock(self):
        self.lock.acquire()
        while self.numberOfReaders > 0 or self.thereIsAWriter:
            self.condition.wait()
        self.thereIsAWriter = True
        self.lock.release()

    def releaseWriteLock(self):
        self.lock.acquire()
        self.thereIsAWriter = False
        self.condition.notify_all()
        self.lock.release()


class RWLock(RWLockWithoutStarvation):
    LIMIT = 5

    def __init__(self):
        super().__init__()
        self.numberOfWritersInWaiting = 0
        self.numberOfIterationsWithoutWriters = 0

    def acquireReadLock(self):
        self.lock.acquire()
        while self.thereIsAWriter or \
                (self.numberOfWritersInWaiting > 0 and self.numberOfIterationsWithoutWriters > self.LIMIT):
            self.condition.wait()
        self.numberOfReaders += 1
        if self.numberOfWritersInWaiting > 0:
            self.numberOfIterationsWithoutWriters += 1
        self.lock.release()

    def releaseReadLock(self):
        self.lock.acquire()
        self.numberOfReaders -= 1
        if self.numberOfReaders == 0:
            self.condition.notify_all()
        self.lock.release()

    def acquireWriteLock(self):
        self.lock.acquire()
        self.numberOfWritersInWaiting += 1
        while self.numberOfReaders > 0 or self.thereIsAWriter:
            self.condition.wait()
        self.thereIsAWriter = True
        self.numberOfWritersInWaiting -= 1
        self.numberOfIterationsWithoutWriters = 0
        self.lock.release()
