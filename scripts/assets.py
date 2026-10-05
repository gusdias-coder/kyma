"""Download selected real Pexels photos. The local seed never needs network access."""
import concurrent.futures, io, json, urllib.request
from pathlib import Path
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'static/images/streetwear'
PHOTOS = [
(16831785,'graphic-back','Ardit Mbrati','back-view-of-a-young-man-wearing-a-graphic-t-shirt'),
(29052570,'graphic-cartoon','Hanna Alves','casual-streetwear-with-cartoon-graphic-t-shirt'),
(31959038,'graphic-red','Ab Pixels','stylish-man-in-vibrant-urban-streetwear'),
(29613985,'graphic-jersey','Rules Effects','young-man-in-urban-outfit-with-graphic-jersey'),
(34421369,'graphic-blue','Fernando Ortiz P.','man-wearing-blue-graphic-tee-in-urban-setting'),
(3799378,'hoodie-black','Ali Pazani','man-in-black-hoodie'),
(19243412,'denim-jacket','Felix Young','woman-wearing-denim-jacket-on-a-street'),
(16069737,'denim-street','Luis Quintero','a-man-wearing-black-t-shirt-and-jeans'),
(5366340,'cargo-street','John Ric Cabatuan','model-in-cargo-pants')]
def download(row):
 photo_id,name,author,slug=row
 url=f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg'
 request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.pexels.com/'})
 with urllib.request.urlopen(request,timeout=45) as response:data=response.read()
 image=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGB')
 image.thumbnail((1800,1800));image.save(OUT/f'{name}.webp','WEBP',quality=86,method=6)
 return dict(id=photo_id,file=f'{name}.webp',photographer=author,source=f'https://www.pexels.com/photo/{slug}-{photo_id}/',download=url,license='https://www.pexels.com/license/',dimensions=list(image.size))
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:entries=list(pool.map(download,PHOTOS))
 (OUT/'sources.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False),encoding='utf-8')
 hoodie=Image.open(OUT/'hoodie-black.webp')
 hoodie.save(OUT.parent/'hero.webp',quality=86)
 ImageOps.fit(hoodie,(700,1050),centering=(.57,.5)).save(OUT.parent/'hero-mobile.webp',quality=85)
 red=Image.open(OUT/'graphic-red.webp')
 ImageOps.fit(red,(1000,1250),centering=(1,.5)).save(OUT/'graphic-red-product.webp',quality=86)
 ImageOps.fit(hoodie,(900,1125),centering=(.57,.5)).save(OUT/'hoodie-black-product.webp',quality=86)
 print(f'{len(entries)} real photographs optimized and attributed.')
