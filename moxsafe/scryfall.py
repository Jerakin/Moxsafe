from pathlib import Path
import requests
import shutil

image_cache = Path("~").expanduser() / ".moxsafe" / "image_cache"
if not image_cache.exists():
    image_cache.mkdir()


def get_image(name):
    image_path = image_cache / f"{name}.png"
    if image_path.exists():
        return image_path
    card = requests.get(f"https://api.scryfall.com/cards/search?q={name}").json()

    # Get the image URL
    if "card_faces" in card['data'][0]:
        img_url = card['data'][0]["card_faces"][0]['image_uris']['normal']
    else:
        img_url = card['data'][0]['image_uris']['normal']
    with image_path.open('wb') as out_file:
        shutil.copyfileobj(requests.get(img_url, stream=True).raw, out_file)
    return image_path
