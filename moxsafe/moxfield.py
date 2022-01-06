import os
import datetime
import requests
import dotenv

_ENDPOINT = 'https://api.moxfield.com/v2/decks/all/'

dotenv.load_dotenv("../.env")


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

        self._content['publicId'] = file_name.stem
        if "commanders" not in self._content:
            self._content["commanders"] = {}
        if "mainboard" not in self._content:
            self._content["mainboard"] = {}
        if "sideboard" not in self._content:
            self._content["sideboard"] = {}
        if "maybeboard" not in self._content:
            self._content["maybeboard"] = {}

        add_to = self._content["mainboard"]
        for line in content.split("\n"):
            if line == "#sideboard":
                add_to = self._content["sideboard"]
            elif line == "#considering":
                add_to = self._content["maybeboard"]
            elif line == "#commanders":
                add_to = self._content["commanders"]
            if line.startswith("#") or not line:
                continue
            quantity, *card_name = line.split(" ")
            add_to[" ".join(card_name)] = {"quantity": int(quantity)}
        return True

    def _board(self, type_):
        main = self._content.get(type_, {})
        return sorted([(data['quantity'], name) for name, data in main.items()], key=lambda x: x[1])

    @property
    def commanders(self):
        return self._board("commanders")

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

        if self.commanders:
            t += "\n#commanders\n"
            for q, n in self.commanders:
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


class Website:
    def __init__(self):
        self._access_token = None
        self._refresh_token = None
        self._token_expiration = None

    def _access(self, response):
        if response.status_code == 200:
            data = response.json()
            self._access_token = data["access_token"]
            self._refresh_token = data["refresh_token"]
            self._token_expiration = datetime.datetime.strptime(data["expiration"], "%Y-%m-%dT%H:%M:%SZ")

    def get_access(self):
        response = requests.post('https://api.moxfield.com/v1/account/token',
                                 json={"userName": os.environ["MOX_USER"], "password": os.environ["MOX_TOKEN"]},
                                 headers={"Content-Type": "application/json;charset=UTF-8"})
        self._access(response)

    def update_access(self):
        response = requests.post('https://api.moxfield.com/v1/account/token/refresh',
                                 json={"refreshToken": self._refresh_token},
                                 headers={"Content-Type": "application/json;charset=UTF-8"})
        self._access(response)

    def bulk_edit(self, deck: Deck):
        if not self._access_token:
            self.get_access()
        elif self._token_expiration < datetime.datetime.now():
            self.update_access()

        data = {"mainboard": "\r\n".join([f"{quantity} {card}" for quantity, card in deck.mainboard]),
                "sideboard": "\r\n".join([f"{quantity} {card}" for quantity, card in deck.sideboard]),
                "maybeboard": "\r\n".join([f"{quantity} {card}" for quantity, card in deck.considering]),
                "playStyle": "paperEuros"}

        response = requests.put(f'https://api.moxfield.com/v2/decks/{deck.id}/bulk-edit',
                                json=data,
                                headers={"Content-Type": "application/json;charset=UTF-8",
                                         f"Authorization": f"Bearer {self._access_token}"})
        return response.status_code == 200
