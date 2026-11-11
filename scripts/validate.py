"""Offline packaging/markup checks. Live Odoo installation is a separate test."""
import ast, json
from pathlib import Path
from lxml import etree, html
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
checks=0
for module in ('ar_pricecut_website','ar_pricecut_demo_catalog'):
    path=ROOT/module
    manifest=ast.literal_eval((path/'__manifest__.py').read_text())
    assert manifest['version']=='19.0.1.0.0'
    for file in manifest.get('data',[]): assert (path/file).is_file();checks+=1
    for files in manifest.get('assets',{}).values():
        for file in files: assert (ROOT/file).is_file();checks+=1
    for file in path.rglob('*.py'): ast.parse(file.read_text());checks+=1
    for file in path.rglob('*.xml'):
        tree=etree.parse(str(file)); checks+=1
        for e in tree.iter():
            for key,value in e.attrib.items():
                if key in ('t-if','t-elif','t-value','t-foreach','t-out','t-field','t-options') or key.startswith('t-att-'):
                    ast.parse(value,mode='eval');checks+=1
            src=e.get('src')
            if src and src.startswith('/ar_pricecut_'):assert (ROOT/src.lstrip('/')).is_file();checks+=1
    for file in (path/'static').rglob('*'):
        if file.is_file() and file.suffix.lower() in ('.png','.jpg','.webp'):
            with Image.open(file) as im:im.verify()
            checks+=1
products=json.loads((ROOT/'ar_pricecut_demo_catalog/data/products.json').read_text())
assert len(products)==12
assert len({p['key'] for p in products})==12
assert {'carib_lager','stag_lager','carib_malta'} <= {p['key'] for p in products}
for p in products:
    assert (ROOT/'ar_pricecut_demo_catalog/static/src/img'/p['image']).is_file()
    assert p['price']>0 and p['category'] in {'pantry','beverages','beer','snacks','personal','household'}
    checks+=1
# Confirm preview pages are free of duplicate IDs, missing local assets and broken local links.
for file in (ROOT/'dist').glob('*.html'):
    tree=html.parse(str(file)); ids=tree.xpath('//@id');assert len(ids)==len(set(ids)),file
    for e in tree.xpath('//*[@src or @href]'):
        link=e.get('src') or e.get('href')
        if not link or link.startswith(('http','tel:','mailto:','#','data:')):continue
        target=link.split('#')[0].split('?')[0]
        assert (ROOT/'dist'/target.lstrip('/')).is_file(), (file,link)
        checks+=1
print(f'PASS: {checks} syntax, manifest, image, catalogue and rendered-link checks; 12 sample products.')
print('Not a live Odoo installation or POS checkout test.')
