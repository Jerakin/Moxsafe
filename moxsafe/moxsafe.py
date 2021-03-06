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
        self.deck = moxfield.Deck()

    def _reload_index(self):
        _git('checkout', 'main')
        with self._index_file.open("r") as fp:
            self._index = json.load(fp)

    def versions(self, deck):
        names = []
        output = subprocess.check_output('git branch -l', shell=True)
        for line in output.decode("utf-8").split("\n"):
            line = line.replace("*", "").strip()
            if deck.id in line:
                names.append(line.replace(f"{deck.id}/", ""))
        return names

    @staticmethod
    def deck_already_exists(deck_id):
        try:
            subprocess.check_output(f'git rev-parse --verify {deck_id}', shell=True, stderr=pipe_to)
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    def get_deck(self, deck_id, version_name="main", at_sha=None):
        if deck_id == self.deck.id and self.deck.version == version_name:
            return self.deck
        if at_sha:
            _git('checkout', at_sha)
        else:
            _git('checkout', f"{deck_id}/{version_name}")
        self.deck = moxfield.Deck(deck_file=repository_path / f"{deck_id}.txt")
        self.deck.version = version_name
        _git('checkout', 'main')
        for deck_entry in self.index:
            if self.deck.id == deck_entry["id"]:
                self.deck._content["name"] = deck_entry["name"]
        return self.deck

    def add_deck(self, deck: moxfield.Deck):
        deck_file = repository_path / f"{deck.id}.txt"
        if self.deck_already_exists(deck.id):
            raise FileExistsError(f"Deck '{deck.name}' with id '{deck.id}' already exists")

        _git('checkout', self._root_sha)
        _git('checkout', '-b', f"{deck.id}/main")

        with deck_file.open("w") as fp:
            fp.write(deck.list)
        _git('add', deck_file.as_posix())
        _git('commit', "-m", f"{deck.name} by {deck.author}")

        # Add to index
        _git('checkout', "main")
        with self._index_file.open("r") as fp:
            self._index = json.load(fp)
        self._index["index"].append({"id": deck.id, "name": deck.name})

        with self._index_file.open("w") as fp:
            json.dump(self._index, fp)

        _git('add', self._index_file.as_posix())
        _git('commit', "-m", f"Updated index with {deck.name}")

    @property
    def index(self):
        return self._index["index"]

    def add_version(self, deck: moxfield.Deck, version_name="main"):
        _git('checkout', self._root_sha)
        _git('checkout', "-b", f"{deck.id}/{version_name}")

        deck_file = repository_path / f"{deck.id}.txt"
        with deck_file.open("w") as fp:
            fp.write(deck.list)
        _git('add', deck_file.as_posix())
        _git('commit', "-m", f"{deck.name} by {deck.author}")

    def add_snapshot(self, deck: moxfield.Deck, comment, active_version="main"):
        deck_file = repository_path / f"{deck.id}.txt"
        old_list = deck.list
        deck.load_from_id(deck.id)
        if old_list == deck.list:
            return
        _git('checkout', f"{deck.id}/{active_version}")
        with deck_file.open("w") as fp:
            fp.write(deck.list)
        _git('add', deck_file.as_posix())
        _git('commit', "-m", comment if comment else "Update")
        _git('checkout', "main")

    def version_history(self, deck, version_name='main'):
        _git('checkout', f"{deck.id}/{version_name}")
        output = subprocess.check_output('git log --format="format:%H$$%cs$$%s%N"', shell=True)
        history = []
        for line in output.decode("utf-8").split("\n"):
            line = line.split('$$')
            if 'initial commit' not in line:
                history.append(line)
        return history

    def delete(self, deck):
        _git("checkout", "main")
        output = subprocess.check_output(f'git branch --list "{deck.id}/*"', shell=True)
        for line in output.decode("utf-8").split("\n"):
            if not line:
                continue
            _git("branch", "-D", f"{line.strip()}")

        for deck_entry in self.index:
            if deck.id == deck_entry["id"]:
                self.index.remove(deck_entry)
                break
        with self._index_file.open("w") as fp:
            json.dump(self._index, fp)
        _git('add', self._index_file.as_posix())
        _git('commit', "-m", f"Removed {deck.name}")

    def update_index(self, deck, index_entry):
        if index_entry["id"] or index_entry["name"]:
            pass
        else:
            return
        for deck_entry in self.index:
            if deck.id == deck_entry["id"]:
                deck_entry["name"] = index_entry["name"] if index_entry["name"] else deck_entry["name"]
                with self._index_file.open("w") as fp:
                    json.dump(self._index, fp)
                _git('add', self._index_file.as_posix())
                _git('commit', "-m", f"Updated index for {deck.name}")
                break


if __name__ == '__main__':
    _deck = moxfield.Deck()
    with (Path(__file__).parent.parent / "burn.json").open() as _fp:
        _deck._content = json.load(_fp)
    _moxsafe = Moxsafe()
    _moxsafe.add_deck(_deck)
