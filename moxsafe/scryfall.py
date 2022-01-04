from pathlib import Path
import requests
import shutil

repository_path = Path("~").expanduser() / ".moxsafe" / "image_cache"


def get_image(name):
    image_path = repository_path / "{name}.png"
    if image_path.exists():
        return image_path
    # Load the card data from Scryfall
    card = requests.get(f"https://api.scryfall.com/cards/search?q={name}").json()

    # Get the image URL
    img_url = card['data'][0]['image_uris']['png']
    with open('image.png', 'wb') as out_file:
        shutil.copyfileobj(requests.get(img_url, stream=True).raw, out_file)
    return image_path
