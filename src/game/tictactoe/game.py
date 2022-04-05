from platform.game import GameBase
import random

class TicTacToe(GameBase):
    def __init__(self, num_players, name_by_id):
        assert num_players == 2, "Invalid number of players"

    def name():
        return "TicTacToe"

    def min_players():
        return 2

    def max_players():
        return 2

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
            if self.board[i][0] == self.board[i][1] == self.board[i][2] \
               and self.board[i][0] != -1:
                return { i: 1 if self.board[i][0] == i else 0
                         for i in range(2) }
            if self.board[0][i] == self.board[1][i] == self.board[2][i] \
               and self.board[0][i] != -1:
                return { i: 1 if self.board[0][i] == i else 0
                         for i in range(2) }

        # Check diagonal
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] \
            or self.board[0][2] == self.board[1][1] == self.board[2][0]) \
            and self.board[1][1] != -1:
            return { i: 1 if self.board[1][1] == i else 0
                     for i in range(2) }

        # Draw
        t = True
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == -1:
                    t = False
            if t == False: break
        if t:
            return { i:i for i in range(2) }

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
