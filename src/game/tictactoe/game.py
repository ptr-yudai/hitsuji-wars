from platform.game import GameBase
import random

class TicTacToe(GameBase):
    def __init__(self, setting):
        assert setting['num_players'] == 2, "Invalid number of players"

    def initialize(self):
        """Initialize this game
        """
        self.board = [
            [-1 for i in range(3)]
            for j in range(3)
        ]
        self.turn = random.randint(0, 1)

    def is_over(self):
        """Check if the game is over

        Returns:
          `is_over` methods must return False if the game is
          still in progress. It must return a list of the scores
          for each player IDs.
        """
        # Check horizontal and vertical
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2]:
                return [ self.board[i][0] ]
            if self.board[0][i] == self.board[1][i] == self.board[2][i]:
                return [ self.board[0][i] ]

        # Check diagonal
        if self.board[0][0] == self.board[1][1] == self.board[2][2] \
           or self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.board[1][1]

        return False

    def update_state(self, pid, inp):
        """Input next move, update state, and reply new public state

        This method is called with input from every player ID for each round.

        Args:
          pid (int): Player ID
          inp (object): Input indicating the next move. You must define
                        the structure of this input and every bot must
                        follow the protocol.
                        Note that this input is sent only by one player.
                        If you need inputs from multiple players to actually
                        step the game, you must check if every player sent
                        the input here.

        Throws:
          If you throw an exception in this method, the sender of this move
          will lose and the game ends.
        """
        assert self.turn == pid
        assert 'x' in inp and inp['x'] in [0, 1, 2], "Invalid position"
        assert 'y' in inp and inp['y'] in [0, 1, 2], "Invalid position"
        x, y = inp['x'], inp['y']

        assert self.board[y][x] == -1, "Already taken by the opponent"

        self.board[y][x] = pid
        self.turn ^= 1

    def share_state(self, pid):
        """Share the current state to a player

        This method is called for every player ID for each round.

        Args:
          pid (int): Player ID to share the state with.
        """
        return self.board

    def next_players(self):
        """Decide next players to receive inputs from

        Returns:
          This method must return a list of player IDs.
        """
        return [ self.turn ]

    def state(self):
        """Return the current state of the game

        The return value of this method will be used
        in the viewer you define. You don't need to
        define this method if you don't implement
        the game viewer.
        """
        return {
            "board": self.board,
            "turn": self.turn
        }

Game = TicTacToe
