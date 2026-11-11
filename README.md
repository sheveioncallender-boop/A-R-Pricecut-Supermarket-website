# A&R Pricecut Supermarket — Odoo 19 Community

Version **19.0.1.0.0** · Developed by **Spxcorp Limited**.

A red-and-navy supermarket website using the supplied A&R logo, real grocery photography and Odoo's native header, mobile navigation, search, shop, product pages, basket, checkout and customer accounts. There is no separate checkout or payment connector.

## Modules

| Folder | Purpose |
| --- | --- |
| `ar_pricecut_website` | Homepage, rotating photo banner, departments, published products with native customer pricing, About, Wholesale, Contact/directions and branded footer. |
| `ar_pricecut_demo_catalog` | Optional 12-product Trinidad sample catalogue with real product images and matching website/POS categories. Installs Point of Sale if needed. |

## CloudPepper installation

1. Add this Git repository to the intended **Odoo 19 Community** instance, branch `main`. Both addon folders are at the repository root.
2. Pull/build the repository and restart Odoo so Python models/controllers are loaded.
3. In developer mode, update the Apps list. Search for **A&R Pricecut Supermarket Website** and install it.
4. With one website, setup selects it automatically. In a multi-website database, open **Website → Configuration → Websites**, choose the intended site and use **Initialize Pricecut Website** in its A&R section. It sets the supplied logo, homepage and navigation once; later upgrades preserve these settings.
5. For the requested sample products, set the intended company's currency to **TTD**, then install **A&R Pricecut — Trinidad Sample Catalogue & POS**. The installer refuses other company currencies rather than changing financial settings or mislabelling prices.
6. Open the website and POS to check the catalogue. If an existing POS has **Restrict Categories** enabled, include the six categories below in its allowed category list. Reload an existing POS session to refresh its product data. The module does not change other POS configurations or open/close sessions.

## Matching categories

| Website category | POS category |
| --- | --- |
| Groceries & Pantry | Groceries & Pantry |
| Beverages | Beverages |
| Beer & Stout | Beer & Stout |
| Snacks & Sweets | Snacks & Sweets |
| Personal Care | Personal Care |
| Household | Household |

Each sample product is published on the selected website, enabled for POS and assigned to its matching categories. Exact existing categories are reused. Some departments intentionally start without sample products. Add your real products to both the eCommerce category and Point of Sale category fields; Odoo treats these as separate fields, not an automatic ongoing sync.

## Sample products

Carib Lager 275ml; Stag Lager 275ml; Carib Malta 275ml; Chubby Grape 250ml; Chubby Banana 250ml; Busta Pear 355ml; Cole Cold Grape 355ml; Oasis Water 500ml; Chief Mutton Curry 85g; Chief Taco Seasoning 40g; Chief Lemon Pepper Seasoning 40g; Chief Rainbow Sprinkles 55g.

Names do not contain “demo”. The optional app and internal product notes identify the sample data. **All sample prices are illustrative TTD amounts, not verified A&R prices.** Products are untracked goods with no quantity adjustments, barcodes, vendor bills or transactions. Sample taxes are empty. Before live trading, review prices, taxes, pack sizes, costs, inventory tracking and real stock, and archive any samples not stocked. Do not treat the sample catalogue as confirmed store availability. Archive samples rather than uninstalling the catalogue once they have been used in orders.

## Contact details and content

- Phone: **+1 (868) 324-3448**, matching the supplied old sign and the public Waze listing.
- Address used: **Eastern Main Road, Sangre Grande, Trinidad and Tobago**. A third-party directory lists #201a; the street number is deliberately omitted until confirmed.
- Hours remain blank: the supplied sign says 7am–10pm, while Waze lists 7am–8pm. The website asks shoppers to call for today's hours. Enter verified hours in the A&R section of the website settings.
- No delivery promise, WhatsApp number, payment acceptance claim, fake reviews or discount percentages are invented.
- Store address, phone and confirmed hours are configurable per website. Corporate/accounting contact records are not overwritten.
- `/contactus` also displays the designed contact page for the branded website. It uses working call/directions links, not an unconfigured email form.

Main URLs: `/pricecut-home`, `/pricecut/about`, `/pricecut/wholesale`, `/pricecut/contact`, `/shop`.

The homepage displays up to eight published, sellable products belonging to this website (or shared products), in Odoo website sequence order. Native `_get_sales_prices()` supplies customer pricelist/tax-aware pricing. Login-only shops do not reveal homepage products. Cards open native product pages so variant choice and availability checks stay in Odoo.

Branding is scoped by `pricecut_enabled`; unrelated websites keep their layout. When disabling or uninstalling the website module, first point its homepage to an existing native page such as `/shop`, and remove/replace the Pricecut navigation links.

## Photography and validation

See [SOURCES.md](SOURCES.md) for photography and business-detail sources. Lifestyle photos are illustrative stock images, not photographs of the actual A&R premises. Product packshots are real manufacturer/retailer images; packaging may differ locally.

`python scripts/build_preview.py` creates a local static design review in `dist/`. This is a **design preview**, not an Odoo runtime: its review header and catalogue interactions are separate from the native Odoo controls installed by the addon. The preview includes the Font Awesome assets in `scripts/preview-assets`; Odoo supplies these itself in production.

`python scripts/validate.py` checks Python/QWeb syntax, addon asset references, image integrity, all 12 catalogue entries and local preview links. `node --check ar_pricecut_website/static/src/js/pricecut.js` checks the hero JavaScript.

The source was checked against Odoo's official 19.0 website, website_sale and point_of_sale models/templates, including the native POS category image field `image_512`. Desktop and mobile design review was performed in a browser. **A live Odoo installation, upgrade and POS sale have not yet been run in a target instance.** Live installation/UAT is the next verification step before launch.
