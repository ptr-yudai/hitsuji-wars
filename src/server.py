#!/usr/bin/env python3
import glob
import importlib.util
import json
import os

class GameManager(object):
    def __init__(self, root_dir:str="game"):
        self.root_dir = root_dir
        self.game_list = []

    def load(self, game_dir:str):
        """Load a single game

        Args:
          game_dir (str): Path to the game folder to import
        """
        if not os.path.isfile(f"{game_dir}/game.json"):
            raise FileNotFoundError(f"'game.json' not found in {game_dir}")
        if not os.path.isfile(f"{game_dir}/game.py"):
            raise FileNotFoundError(f"'game.py' not found in {game_dir}")

        # Load config
        with open(f"{game_dir}/game.json", "r") as f:
            info = json.load(f)

        # Import game
        module_name = f"{game_dir.replace('/', '.')}.game"
        self.game_list.append(
            importlib.import_module(module_name).Game
        )

    def load_all(self):
        """Load every game from game root directory
        """
        for game_dir in glob.iglob(f"{self.root_dir}/*"):
            if not os.path.isdir(game_dir): continue
            try:
                self.load(game_dir)
            except Exception as e:
                print(f"[-] Could not load a game: {e}")

if __name__ == '__main__':
    gm = GameManager()
    gm.load_all()
