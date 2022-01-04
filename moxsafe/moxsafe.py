import json
import os
import subprocess
from pathlib import Path

import moxfield

repository_path = Path("~").expanduser() / ".moxsafe" / "repository"

pipe_to = subprocess.DEVNULL


def _git(*args):
    subprocess.run(['git'] + list(args), stdout=pipe_to, stderr=pipe_to)


class Moxsafe:
    def __init__(self):
        self._index_file = repository_path / "index.json"
        self._root_sha = None
        self._index = None
        if not repository_path.exists():
            repository_path.mkdir(parents=True)
            os.chdir(repository_path)

            _git('init')

            with self._index_file.open("w") as fp:
                json.dump({"index": []}, fp)
            _git('add', self._index_file.as_posix())
            _git('commit', "-m", "initial commit")
            _git('config', "advice.detachedHead", "false")

        os.chdir(repository_path)
        _git('checkout', 'main')

        output = subprocess.check_output('git log --reverse --format=format:%H', shell=True)
        self._root_sha = output.split(b"\n")[0].decode("utf-8")
        self._reload_index()

    def _reload_index(self):
        _git('checkout', 'main')
        with self._index_file.open("r") as fp:
            self._index = json.load(fp)

    @staticmethod
    def deck_already_exists(deck_id):
        try:
            subprocess.check_output(f'git rev-parse --verify {deck_id}', shell=True, stderr=pipe_to)
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    @staticmethod
    def get_deck(deck_id):
        _git('checkout', deck_id)
        deck = moxfield.Deck(deck_file=repository_path / f"{deck_id}.txt")
        _git('checkout', 'main')
        return deck

    def add_deck(self, deck: moxfield.Deck):
        deck_file = repository_path / f"{deck.id}.txt"
        if self.deck_already_exists(deck.id):
            raise FileExistsError(f"Deck '{deck.name}' with id '{deck.id}' already exists")

        _git('checkout', self._root_sha)
        _git('checkout', '-b', deck.id)

        with deck_file.open("w") as fp:
            fp.write(deck.list)
        _git('add', deck_file)
        _git('commit', "-m", f"{deck.name} by {deck.author}")

        # Add to index
        _git('checkout', "main")
        with self._index_file.open("r") as fp:
            self._index = json.load(fp)
        self._index["index"].append({"id": deck.id, "name": deck.name})

        with self._index_file.open("w") as fp:
            json.dump(self._index, fp)

        _git('add', self._index_file)
        _git('commit', "-m", f"Updated index with {deck.name}")

    @property
    def index(self):
        return self._index["index"]

    def add_version(self, deck: moxfield.Deck, comment):
        deck_file = repository_path / f"{deck.id}.txt"
        old_list = deck.list
        deck.load_from_id(deck.id)
        if old_list == deck.list:
            return
        _git('checkout', deck.id)
        with deck_file.open("w") as fp:
            fp.write(deck.list)
        _git('add', deck_file)
        _git('commit', "-m", comment if comment else "Update")
        _git('checkout', "main")


if __name__ == '__main__':
    _deck = moxfield.Deck()
    with (Path(__file__).parent.parent / "burn.json").open() as _fp:
        _deck._content = json.load(_fp)
    _moxsafe = Moxsafe()
    _moxsafe.add_deck(_deck)
