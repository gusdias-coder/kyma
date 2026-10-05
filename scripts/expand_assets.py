"""Acquire real reference photos found in the public Pexels search pages."""
import concurrent.futures
import io
import json
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'static/images/expanded'
PHOTOS = [
    (32969128, 'Cesar O Neill', 'jpeg'), (39185960, 'Jose Ismael Espinola', 'jpeg'),
    (5692478, 'Luis Quintero', 'jpeg'), (5236997, 'cottonbro studio', 'jpeg'),
    (38574763, 'Mc Follis', 'jpeg'), (12204428, 'Lucretius Mooka', 'jpeg'),
    (4227116, 'Zulurid', 'jpeg'), (10619446, 'cottonbro studio', 'jpeg'),
    (12101739, 'Leonardo Moncao', 'jpeg'), (17562577, 'Dmitry Ovsyannikov', 'jpeg'),
    (15965650, 'Lucas Brown', 'png'), (16863982, 'Tony Boyd', 'jpeg'),
    (13598018, 'Luke Landon', 'jpeg'), (32969104, 'Cesar O Neill', 'jpeg'),
    (15127181, 'Aleks Magnusson', 'jpeg'), (19392467, 'Mutecevvil', 'jpeg'),
    (12821063, 'Marcus Queiroga Silva', 'jpeg'), (896293, 'Godisable Jacob', 'jpeg'),
    (9476367, 'Mikhail Nilov', 'jpeg'), (33549618, 'Michael Obstoj', 'jpeg'),
    (39296596, 'Mauricio Garcia', 'jpeg'), (15959737, 'Omran Soliman', 'jpeg'),
    (32219977, 'Khalifa Yahaya', 'jpeg'),
]

def download(row):
    photo_id, author, extension = row
    url = f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.{extension}?auto=compress&cs=srgb&w=1100'
    target = OUT / f'photo-{photo_id}.webp'
    if not target.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as response:
            data = response.read()
        photo = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGB')
        photo.thumbnail((1100, 1400))
        photo.save(target, 'WEBP', quality=85, method=6)
    street = {32969128,39185960,5692478,5236997,38574763,12204428,15965650,16863982,13598018,32969104,15127181,19392467,12821063}
    return {'id': photo_id, 'file': target.name, 'photographer': author,
            'source': 'https://www.pexels.com/search/streetwear/' if photo_id in street else 'https://www.pexels.com/search/fashion/', 'download': url,
            'license': 'https://www.pexels.com/license/'}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        entries = list(pool.map(download, PHOTOS))
    (OUT / 'sources.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    sheet = Image.new('RGB', (1100, 5 * 270), '#eeeeea')
    draw = ImageDraw.Draw(sheet)
    for index, entry in enumerate(entries):
        tile = ImageOps.fit(Image.open(OUT / entry['file']), (210, 238))
        left, top = (index % 5) * 220, (index // 5) * 270
        sheet.paste(tile, (left, top))
        draw.text((left + 8, top + 246), str(entry['id']), fill='black')
    sheet.save(ROOT / 'docs/screenshots/expanded-photo-selection.jpg', quality=88)
    print(f'{len(entries)} real photographs ready for visual selection.')
