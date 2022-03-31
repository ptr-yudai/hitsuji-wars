from abc import ABCMeta, abstractmethod

class GameBase(metaclass=ABCMeta):
    @abstractmethod
    def state(self) -> object:
        pass
