"""Static design preview from the actual QWeb content; not an Odoo runtime test."""
from pathlib import Path
from types import SimpleNamespace
from lxml import etree
import datetime, json, html, re, shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'scripts/preview-assets', OUT/'assets', dirs_exist_ok=True)
for module in ('ar_pricecut_website', 'ar_pricecut_demo_catalog'):
    shutil.copytree(ROOT/module/'static', OUT/module/'static', dirs_exist_ok=True)
templates = {e.get('id'): e for e in etree.parse(str(ROOT/'ar_pricecut_website/views/templates.xml')).getroot()}
class Record(SimpleNamespace):
    def __getitem__(self, key): return getattr(self,key)
class Currency:
    def is_zero(self, x): return x == 0
site=Record(name='A&R Pricecut Supermarket',pricecut_phone='+1 (868) 324-3448', pricecut_address='Eastern Main Road, Sangre Grande, Trinidad and Tobago', pricecut_hours=False, pricecut_enabled=True, prevent_zero_price_sale=False,currency_id=Currency(),_pricecut_phone_uri=lambda:'tel:+18683243448')
items=json.loads((ROOT/'ar_pricecut_demo_catalog/data/products.json').read_text())
products=[Record(id=i+1,name=p['name'],website_url='product-'+p['key']+'.html',image='/ar_pricecut_demo_catalog/static/src/img/'+p['image'],price=p['price']) for i,p in enumerate(items)]
prices={p.id:{'price_reduce':p.price} for p in products}
departments=[dict(name=n,url='shop.html?category='+k,image='/ar_pricecut_website/static/src/img/'+im) for k,n,im in [('pantry','Groceries & Pantry','cat_pantry_hd.webp'),('beverages','Beverages','cat_beverages_hd.webp'),('beer','Beer & Stout','cat_beverages_hd.webp'),('snacks','Snacks & Sweets','cat_snacks_hd.webp'),('personal','Personal Care','cat_personal_hd.webp'),('household','Household','cat_household_hd.webp')]]
ctx=dict(website=site,datetime=datetime,departments=departments,products=products[:8],product_prices=prices,can_shop=True)
def esc(s): return html.escape(str(s),quote=True)
def evaluate(s,c):return eval(s,{'__builtins__':{}},c)
def children(n,c):
    out=esc(n.text or ''); branch=False; matched=False
    for ch in n:
        if not isinstance(ch.tag,str):continue
        attrs=ch.attrib
        if 't-if' in attrs:
            branch=True;matched=bool(evaluate(attrs['t-if'],c)); run=matched
        elif 't-elif' in attrs:
            run=branch and not matched and bool(evaluate(attrs['t-elif'],c));matched=matched or run
        elif 't-else' in attrs:
            run=branch and not matched;matched=True
        else: branch=False;matched=False;run=True
        if run:out+=render(ch,c,True)
        out+=esc(ch.tail or '')
    return out

def render(n,c,condition_handled=False):
    a=n.attrib
    if not condition_handled and 't-if' in a and not evaluate(a['t-if'],c):return ''
    if 't-foreach' in a:
        out=''
        for x in evaluate(a['t-foreach'],c):
            nc=dict(c);nc[a['t-as']]=x
            copy=etree.fromstring(etree.tostring(n));copy.attrib.pop('t-foreach');copy.attrib.pop('t-as');out+=render(copy,nc,True)
        return out
    if 't-set' in a:
        c[a['t-set']]=evaluate(a['t-value'],c) if 't-value' in a else ''.join(n.itertext());return ''
    if 't-call' in a:
        if a['t-call']=='website.layout':return children(n,dict(c))
        return children(templates[a['t-call'].split('.')[-1]],dict(c))
    content=children(n,c)
    val=a.get('t-out',a.get('t-field'))
    if val:
        v=evaluate(val,c);content='TT$ '+f'{v:.2f}' if 'monetary' in a.get('t-options','') else esc(v)
    if n.tag in ('t','template'):return content
    attrs={k:v for k,v in a.items() if not k.startswith('t-')}
    for k,v in a.items():
        if k.startswith('t-att-'):
            result=evaluate(v,c)
            if result is not None and result is not False:attrs[k[6:]]=str(result)
    if n.tag=='img' and attrs.get('src','').startswith('/web/image/product.template/'):
        pid=int(attrs['src'].split('/')[4]);attrs['src']=products[pid-1].image
    if 'href' in attrs:
        routes={'/':'index.html','/pricecut-home':'index.html','/pricecut/about':'about.html','/pricecut/wholesale':'wholesale.html','/pricecut/contact':'contact.html','/shop':'shop.html'}
        href=attrs['href'];path,*anchor=href.split('#',1)
        if path in routes:attrs['href']=routes[path]+('#'+anchor[0] if anchor else '')
        if href.startswith('/my/') or href.startswith('/shop/cart'):attrs['href']='shop.html'
    result='<'+n.tag+''.join(' '+k+'="'+esc(v)+'"' for k,v in attrs.items())+'>'
    return result if n.tag in ('img','input','meta','link','br','hr') else result+content+'</'+n.tag+'>'

HEADER='''<aside class="preview-note">DESIGN PREVIEW · Sample catalogue · Live shopping runs in Odoo</aside><header id="top"><div class="preview-nav pc-container"><button class="preview-toggle" aria-label="Toggle navigation" aria-expanded="false">☰</button><a class="navbar-brand" href="index.html"><img src="/ar_pricecut_website/static/src/img/pricecut-logo.png" alt="A&R Pricecut Supermarket"/></a><nav class="preview-links"><a href="index.html">Home</a><a href="shop.html">Shop</a><a href="index.html#departments">Departments</a><a href="wholesale.html">Wholesale</a><a href="about.html">About</a><a href="contact.html">Contact</a></nav><a class="preview-cart" href="shop.html" aria-label="Browse sample shop"><i class="fa fa-shopping-basket"></i></a></div></header>'''
EXTRA='''.preview-note{background:#f1f3f8;color:#697087;font:10px Arial;padding:7px;text-align:center;letter-spacing:.05em}.preview-nav{position:relative;display:flex;align-items:center;gap:32px;min-height:90px}.preview-links{display:flex;gap:24px;margin-left:auto}.preview-links a{font-size:13px;font-weight:bold;color:#09164b}.preview-cart{background:#fff0f2;color:#e60019;padding:14px;border-radius:50%}.preview-toggle{display:none;background:none;border:0;font-size:23px}.preview-search{padding:15px;border:1px solid #ddd;border-radius:5px;width:100%;margin-bottom:25px}.pc-product[hidden]{display:none}@media(max-width:991px){.preview-toggle{display:block}.preview-nav{justify-content:space-between;gap:20px;min-height:75px}.preview-links{display:none;position:absolute;top:100%;left:0;right:0;background:white;padding:24px;box-shadow:0 8px 15px #0001;flex-direction:column}.preview-links.open{display:flex;z-index:100}.preview-nav .navbar-brand{margin:0 auto}}'''
SCRIPT='''document.querySelector('.preview-toggle')?.addEventListener('click',function(){let n=document.querySelector('.preview-links');n.classList.toggle('open');this.setAttribute('aria-expanded',n.classList.contains('open'))});const cat=new URLSearchParams(location.search).get('category');const filter=()=>{const q=document.querySelector('.preview-search')?.value.toLowerCase()||'';document.querySelectorAll('.pc-product').forEach(p=>p.hidden=(!!cat&&p.dataset.category!==cat)||!p.textContent.toLowerCase().includes(q))};document.querySelector('.preview-search')?.addEventListener('input',filter);if(document.querySelector('.preview-search'))filter();'''
def page(body,title):return '<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>'+esc(title)+' | A&R Pricecut Preview</title><link rel="stylesheet" href="/assets/font-awesome.css"/><link rel="stylesheet" href="/ar_pricecut_website/static/src/css/pricecut.css"/><style>body{margin:0}'+EXTRA+'</style></head><body><div class="pc-website">'+children(templates['topbar'],dict(ctx))+HEADER+body+children(templates['footer'],dict(ctx))+'</div><script src="/ar_pricecut_website/static/src/js/pricecut.js"></script><script>'+SCRIPT+'</script></body></html>'
for template,name,title in [('homepage','index','Home'),('about_page','about','About'),('wholesale_page','wholesale','Wholesale'),('contact_page','contact','Contact')]:
    (OUT/(name+'.html')).write_text(page(children(templates[template],dict(ctx)),title))
cards=[]
for p,item in zip(products,items):
    cards.append('<article class="pc-product" data-category="'+item['category']+'"><a href="'+p.website_url+'" class="pc-product-image"><img src="'+p.image+'" alt="'+esc(p.name)+'"/></a><a href="'+p.website_url+'" class="pc-product-name">'+esc(p.name)+'</a><div class="pc-product-bottom"><strong>TT$ '+f'{p.price:.2f}'+'</strong><a href="'+p.website_url+'" class="pc-product-view">→</a></div></article>')
    body='<main class="pc-container pc-section"><a href="shop.html" class="pc-text-link">← Back to sample catalogue</a><div class="pc-story" style="padding-top:25px"><img style="width:100%;height:400px;object-fit:contain" src="'+p.image+'" alt="'+esc(p.name)+'"/><div><span class="pc-eyebrow">SAMPLE CATALOGUE</span><h1>'+esc(p.name)+'</h1><h2>TT$ '+f'{p.price:.2f}'+'</h2><p>Illustrative price for review. In Odoo, this product uses the native product page, basket and checkout.</p><a href="contact.html" class="pc-button">Contact the store</a></div></div></main>'
    (OUT/p.website_url).write_text(page(body,p.name))
body='<main class="pc-container pc-section"><span class="pc-eyebrow">TRINIDAD FAVOURITES</span><h1>Explore the shop.</h1><p>Sample products and illustrative TTD prices for design review.</p><input class="preview-search" type="search" placeholder="Search sample products" aria-label="Search sample products"/><div class="pc-products">'+''.join(cards)+'</div></main>'
(OUT/'shop.html').write_text(page(body,'Shop'))
(ROOT/'.openai').mkdir(exist_ok=True)
(ROOT/'.openai/hosting.json').write_text(json.dumps({'static':{'directory':'dist'}}))
print(f'Rendered {len(products)+5} preview pages in {OUT}')
