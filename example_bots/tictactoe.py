from common_wrapper import *
import json
import os
import random

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 18880))

sock = Socket(HOST, PORT)

# Join game
sock.join(game="TicTacToe")

# Start game
while True:
    t, data = sock.recv_data()
    print(t, data)
    if t == 'gameover':
        if data: break

    elif t == 'turn':
        if data:
            while True:
                x, y = [random.randint(0, 2) for i in range(2)]
                if board[y][x] == -1:
                    break
            sock.send_data({'x': x, 'y': y})

    elif t == 'state':
        board = data

    elif t == 'meta':
        # TODO: 何人いるピヨか？とか
        print("Registered")

    else:
        raise ValueError("WTF")

sock.close()
