import requests

_ENDPOINT = 'https://api.moxfield.com/v2/decks/all/'


class Deck:
    def __init__(self, *, deck_id=None, deck_file=None):
        if deck_id and deck_file:
            raise ValueError("Multiple mutually exclusive arguments used")

        self._content = {}
        if deck_id:
            self.load_from_id(deck_id)
        if deck_file:
            self.load_from_file(deck_file)

    def load_from_id(self, deck_id):
        r = requests.get(_ENDPOINT + deck_id)
        if r.status_code == 200:
            self._content = r.json()
            return True
        return False

    def load_from_file(self, file_name):
        with file_name.open() as fp:
            content = fp.read()

        if "mainboard" not in self._content:
            self._content["mainboard"] = {}
        if "sideboard" not in self._content:
            self._content["sideboard"] = {}
        if "maybeboard" not in self._content:
            self._content["maybeboard"] = {}

        add_to = self._content["mainboard"]
        for line in content.split("\n"):
            if line.startswith("#") or not line:
                continue
            quantity, *card_name = line.split(" ")
            add_to[" ".join(card_name)] = {"quantity": quantity}
            if line == "#sideboard":
                add_to = self._content["sideboard"]
            elif line == "#considering":
                add_to = self._content["maybeboard"]
        return True

    def _board(self, type_):
        main = self._content.get(type_, {})
        return sorted([(data['quantity'], name) for name, data in main.items()], key=lambda x: x[1])

    @property
    def mainboard(self):
        return self._board("mainboard")

    @property
    def sideboard(self):
        return self._board("sideboard")

    @property
    def considering(self):
        return self._board("maybeboard")

    @property
    def list(self):
        t = ""
        if self.mainboard:
            for q, n in self.mainboard:
                t += f"{q} {n}\n"

        if self.sideboard:
            t += "\n#sideboard\n"
            for q, n in self.sideboard:
                t += f"{q} {n}\n"

        if self.considering:
            t += "\n#considering\n"
            for q, n in self.considering:
                t += f"{q} {n}\n"
        return t

    @property
    def id(self):
        return self._content.get("publicId", None)

    @property
    def name(self):
        return self._content.get("name", None)

    @property
    def author(self):
        return self._content.get("createdByUser", {}).get("userName", "?")
