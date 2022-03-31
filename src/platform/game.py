from abc import ABCMeta, abstractmethod
from typing import Union, List

"""Game Manager Overview
game.initialize(setting)
while game.is_over() == False:

  for pid in players:
    send_to_player(pid, game.share_state(pid))

  for pid in game.next_players():
    game.update_state(np, receive_from_player(pid))
"""

class GameBase(metaclass=ABCMeta):
    def state(self) -> object:
        raise NotImplementedError("'state' is not implemented in this game")

    @abstractmethod
    def initialize(self, setting:object):
        pass

    @abstractmethod
    def update_state(self, pid:int, inp:object):
        pass

    @abstractmethod
    def share_state(self, pid:int) -> object:
        pass

    @abstractmethod
    def next_players(self) -> List[int]:
        pass

    @abstractmethod
    def is_over(self) -> Union[bool, List[int]]:
        pass
