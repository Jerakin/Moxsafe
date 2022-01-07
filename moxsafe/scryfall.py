from pathlib import Path
import requests
import shutil
import base64

image_cache = Path("~").expanduser() / ".moxsafe" / "image_cache"
if not image_cache.exists():
    image_cache.mkdir()


def get_image(name):
    b_name = name.encode('utf-8')
    image_path = image_cache / f"{base64.urlsafe_b64encode(b_name)}.png"
    if image_path.exists():
        return image_path
    card = requests.get(f"https://api.scryfall.com/cards/named?exact={name}").json()

    # Get the image URL
    if "card_faces" in card:
        img_url = card["card_faces"][0]['image_uris']['normal']
    else:
        img_url = card['image_uris']['normal']
    with image_path.open('wb') as out_file:
        shutil.copyfileobj(requests.get(img_url, stream=True).raw, out_file)
    return image_path
