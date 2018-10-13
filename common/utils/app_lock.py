from abc import ABCMeta, abstractmethod


class AppLock(metaclass=ABCMeta):

    @abstractmethod
    def lock(self):
        pass

    @abstractmethod
    def unlock(self):
        pass
