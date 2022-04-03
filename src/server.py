#!/usr/bin/env python3
import glob
import importlib
import json
import os
import selectors
import socket
import threading
from console.logger import logger
from mutex.rwlock import ReadWriteLock
from platform.game import GameBase
from typing import Any, NewType

GameConstructor = NewType("GameConstructor", Any)
logger.level = 3

HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', '18880'))

def recvline(sock) -> bytes:
    """Receive a line of data

    Receive data from a socket until it reads '\n'
    """
    data = b''
    while True:
        c = sock.recv(1)
        if c == b'':
            raise ConnectionRefusedError("Connection closed from client")
        if c == b'\n':
            break
        data += c
    return data

def sendline(sock, raw):
    assert b'\n' not in raw, "Do not include newline"
    sock.sendall(raw + b'\n')

def recv_data(sock):
    """Receive a JSON data
    """
    return json.loads(recvline(sock).decode())

def send_data(sock, data):
    """Send data to client
    """
    payload = {'result': 'success', 'data': data}
    sendline(sock, json.dumps(payload).encode())

def send_error(sock, msg):
    """Send error message to client
    """
    data = {'result': 'error', 'reason': msg}
    sock.sendall(json.dumps(data).encode())
    sock.close()
    raise Exception(msg)

known_games: dict[str, GameConstructor] = {}
known_games_lock = ReadWriteLock()

connections = {}
connections_lock = ReadWriteLock()

def start_game(game_class: GameConstructor, players):
    """Game manager

    Start a new game
    """
    num_players = len(players)
    name_by_id = {pid: player[0] for pid, player in enumerate(players)}
    sock_by_id = {pid: player[1] for pid, player in enumerate(players)}

    # Initialize game
    game = game_class(num_players, name_by_id)
    game.initialize()

    # Game loop
    logger.info(f"New game started: {game_class.name()}")
    logger.info(f"Players:")
    for pid in range(num_players):
        logger.info(f"- {name_by_id[pid]}")

    while not game.is_over():
        # Share current state
        for pid in range(num_players):
            state = game.share_state(pid)
            logger.debug(f"Sharing state with {name_by_id[pid]}: {state}")
            send_data(sock_by_id[pid], state)

        # Ask next move
        # TODO
        break

    # Game over
    # TODO

def handle_connection(sock, client_host: str):
    """Handle new connection from client
    """
    try:
        # Receive client data
        data = json.loads(recvline(sock).decode())
        if 'game' not in data:
            send_error(sock, "Game not specified")
        if 'name' not in data:
            send_error(sock, "Your name not given")
        if not isinstance(data['game'], str):
            send_error(sock, "Game name must be string")
        if not isinstance(data['name'], str):
            send_error(sock, "Client name must be string")

        game = data["game"]
        name = data["name"]

        # Lookup game
        known_games_lock.acquire_read()
        is_known_game = game in known_games
        known_games_lock.release_read()
        if not is_known_game:
            send_error(sock, f"Game '{data['game']}' not found")

        # If everything is valid, add to client list
        connections_lock.acquire_write()
        if game not in connections:
            connections[game] = []
        connections[game].append((name, sock))

        # Notify the bot that it's registered
        send_data(sock, "Registered")

        # Check if we can start the game
        cnt = known_games[game].min_players()
        if len(connections[game]) >= cnt:
            # Pass to game manager
            threading.Thread(
                target=start_game,
                args=(known_games[game], connections[game][:cnt])
            ).start()
            connections[game] = connections[game][cnt:]
        connections_lock.release_write()

    except Exception as e:
        logger.error(f"Error: {e} (Connection closed: {client_host})")
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
    game_class = importlib.import_module(module_name).Game

    return game_class

def load_all(root_dir: str) -> dict[str, GameConstructor]:
    """Load every game from game root directory
    """
    known_games = {}

    # Strip the leading './'
    if root_dir.startswith("./"):
        root_dir = root_dir[2:]

    for game_dir in glob.iglob(f"{root_dir}/*"):
        if not os.path.isdir(game_dir): continue
        try:
            game = load_game(game_dir)
            known_games[game.name()] = game
        except Exception as e:
            logger.error(f"Could not load a game: {e}")

    return known_games

def main():
    global known_games
    known_games = load_all("./game/")

    # Setup socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('0.0.0.0', PORT))
    s.setblocking(False)
    s.listen(128)

    selector = selectors.DefaultSelector()
    selector.register(s, selectors.EVENT_READ)

    while True:
        events = selector.select()
        for key, _ in events:
            sock, addr = key.fileobj.accept()
            logger.debug(f"New connection from {addr[0]}:{addr[1]}")

            threading.Thread(target=handle_connection, args=(sock, addr)).start()

if __name__ == '__main__':
    main()
