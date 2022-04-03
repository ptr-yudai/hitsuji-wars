#!/usr/bin/env python3
import glob
import importlib
import json
import os
import socket, threading
from logging import getLogger, StreamHandler, DEBUG
import selectors
import json
from platform.game import GameBase
from typing import Any, NewType

GameConstructor = NewType("GameConstructor", Any)


PORT = 18880
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

def recv(sock) -> bytes:
    return sock.recv(4096)

def recv_data(sock):
    return json.loads(recv(sock).decode())

def send_data(sock, msg):
    sock.sendall(json.dumps(msg).encode())


# https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s04.html
class ReadWriteLock():
    """ A lock object that allows many simultaneous "read locks", but
    only one "write lock." """

    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    def acquire_read(self):
        """ Acquire a read lock. Blocks only if a thread has
        acquired the write lock. """
        self._read_ready.acquire()
        try:
            self._readers += 1
        finally:
            self._read_ready.release()

    def release_read(self):
        """ Release a read lock. """
        self._read_ready.acquire()
        try:
            self._readers -= 1
            if not self._readers:
                self._read_ready.notifyAll()
        finally:
            self._read_ready.release()

    def acquire_write(self):
        """ Acquire a write lock. Blocks until there are no
        acquired read or write locks. """
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
        """ Release a write lock. """
        self._read_ready.release()


known_games: dict[str, GameConstructor] = {}
known_games_lock = ReadWriteLock()

connections = {}
connections_lock = ReadWriteLock()

def start_game(game_class: GameConstructor, players):
    sock_by_id = {player[0]:player[1] for player in players}

    # initialize
    game = game_class(list(sock_by_id.keys()))
    msgs = game.init()

    for player_id, msg in msgs.items():
        send_data(sock_by_id[player_id], msg)

    selector = selectors.DefaultSelector()
    for player_id, sock in sock_by_id.items():
        selector.register(sock, selectors.EVENT_READ, data=player_id)

    # main loop
    while True:
        # polling for sending messege from them
        events = selector.select()
        for key, _ in events:
            try:
                sock, action_player = key.fileobj, key.data
                data = recv_data(sock)  # dataが受信できていないときはsocketがcloseしてるのでshutdownしにいく

                # TODO
                if game.is_over():
                    pass
            except Exception as e :
                logger.debug("error {}".format(e))

    msgs = game.finish()
    for player_id, msg in msgs.items():
        send_data(sock_by_id[player_id], msg)
        sock_by_id[player_id].close()


def handle_connection(sock):
    buf = recv(sock)
    try:
        # data = { name, game }
        data = json.loads(buf.decode())
        game = data["game"]
        name = data["name"]

        known_games_lock.acquire_read()
        is_known_game = game in known_games
        known_games_lock.release_read()
        if not is_known_game:
            logger.debug("unknown game {}. connection close.".format(data["game"]))
            sock.close()
            return

        connections_lock.acquire_write()
        if game not in connections:
            connections[game] = []
        connections[game].append((name, sock))

        cnt = known_games[game].PLAYER_COUNT
        if len(connections[game]) >= cnt:
            # 十分なプレイヤーが集まったのでゲーム用のスレッドを建ててそちらに任せる
            threading.Thread(target=start_game, args=(known_games[game], connections[game][:cnt])).start()
            connections[game] = connections[game][cnt:]
        connections_lock.release_write()

    except Exception as e:
        logger.debug("invalid data. connection close {}".format(e))
        sock.close()
        return

def load_game(game_dir: str) -> GameConstructor:
    """Load a single game

    Args:
      game_dir (str): Path to the game folder to import
    """
    if not os.path.isfile(f"{game_dir}/game.py"):
        raise FileNotFoundError(f"'game.py' not found in {game_dir}")

    # Import game
    module_name = f"{game_dir.replace('/', '.')}.game"
    return importlib.import_module(module_name).Game

def load_all(root_dir: str) -> dict[str, GameConstructor]:
    """Load every game from game root directory
    """
    known_games = {}
    for game_dir in glob.iglob(f"{root_dir}/*"):
        if not os.path.isdir(game_dir): continue
        try:
            game = load_game(game_dir)
            known_games[game.name()] = game
        except Exception as e:
            print(f"[-] Could not load a game: {e}")
    return known_games

def main():
    global known_games
    known_games = load_game("./game/")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', PORT))
    s.setblocking(False)
    s.listen(128)

    selector = selectors.DefaultSelector()
    selector.register(s, selectors.EVENT_READ)

    while True:
        events = selector.select()
        for key, _ in events:
            sock, addr = key.fileobj.accept()
            sock.setblocking(False)
            logger.debug("connection from {}".format(addr))

            threading.Thread(target=handle_connection, args=(sock,)).start()

if __name__ == '__main__':
    main()
