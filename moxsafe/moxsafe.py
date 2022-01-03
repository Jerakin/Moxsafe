import json
import os
import subprocess
from pathlib import Path

import moxfield

repository_path = Path("~").expanduser() / ".moxsafe" / "repository"

pipe_to = subprocess.DEVNULL


def _git(*args):
    subprocess.run(['git'] + args, stdout=pipe_to)


class Moxsafe:
    def __init__(self):
        self.index_file = repository_path / "index.json"
        self.root_sha = None
        if not repository_path.exists():
            repository_path.mkdir(parents=True)
            os.chdir(repository_path)

            subprocess.run(['git', 'init'])

            with self.index_file.open("w") as fp:
                json.dump({"index": []}, fp)

            subprocess.run(['git', 'add', self.index_file.as_posix()], stdout=pipe_to)
            subprocess.run(['git', 'commit', "-m", "initial commit"], stdout=pipe_to)
            subprocess.run(['git', 'config', "advice.detachedHead", "false"], stdout=pipe_to)

        os.chdir(repository_path)
        subprocess.run(['git', 'checkout', 'main'])
        output = subprocess.check_output(" ".join(['git', 'log', '--reverse', '--format=format:%H']), shell=True)
        self.root_sha = output.split(b"\n")[0].decode("utf-8")

    @staticmethod
    def deck_already_exists(deck_id):
        try:
            subprocess.check_output(" ".join(['git', 'rev-parse', '--verify', deck_id]), shell=True)
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    def add_deck(self, deck: moxfield.Deck):
        deck_file = repository_path / f"{deck.id}.txt"
        if self.deck_already_exists(deck.id):
            raise FileExistsError(f"Deck '{deck.name}' with id '{deck.id}' already exists")

        subprocess.run(['git', 'checkout', self.root_sha])
        subprocess.run(['git', 'checkout', '-b', deck.id])

        with deck_file.open("w") as fp:
            fp.write(deck.list)
        subprocess.run(['git', 'add', deck_file])
        subprocess.run(['git', 'commit', "-m", f"{deck.name} by {deck.author}"])

        # Add to index
        subprocess.run(['git', 'checkout', "main"])
        with self.index_file.open("r") as fp:
            index = json.load(fp)
        index["index"].append({"id": deck.id, "name": deck.name})

        with self.index_file.open("w") as fp:
            json.dump(index, fp)

        subprocess.run(['git', 'add', self.index_file])
        subprocess.run(['git', 'commit', "-m", f"Updated index with {deck.name}"])

    def add_version(self, deck_id):
        pass


if __name__ == '__main__':
    _deck = moxfield.Deck()
    with (Path(__file__).parent.parent / "bogles.json").open() as _fp:
        _deck._content = json.load(_fp)
    _moxsafe = Moxsafe()
    _moxsafe.add_deck(_deck)
