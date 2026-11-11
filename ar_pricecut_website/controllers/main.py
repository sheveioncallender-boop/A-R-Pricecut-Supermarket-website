from odoo import http
from odoo.fields import Domain
from odoo.http import request
from werkzeug.exceptions import NotFound


class PricecutWebsite(http.Controller):
    _departments = (
        ('Groceries & Pantry', ('Groceries & Pantry', 'Pantry', 'Groceries'), 'cat_pantry_hd.webp', 'Pantry'),
        ('Beverages', ('Beverages', 'Drinks'), 'cat_beverages_hd.webp', 'Beverages'),
        ('Beer & Stout', ('Beer & Stout', 'Beer', 'Beers'), 'cat_beverages_hd.webp', 'Beer'),
        ('Snacks & Sweets', ('Snacks & Sweets', 'Snacks'), 'cat_snacks_hd.webp', 'Snacks'),
        ('Personal Care', ('Personal Care', 'Personal Care & Beauty'), 'cat_personal_hd.webp', 'Personal Care'),
        ('Household', ('Household', 'Home & Kitchen'), 'cat_household_hd.webp', 'Household'),
    )

    def _check_website(self):
        if not request.website.pricecut_enabled:
            raise NotFound()

    def _category_tiles(self):
        website = request.website
        Category = request.env['product.public.category']
        categories = Category.with_context(lang='en_US').search(Domain(website.website_domain()))
        tiles = []
        from urllib.parse import urlencode
        for label, aliases, image, search in self._departments:
            matching = categories.filtered(lambda c: c.name in aliases)
            category = matching.filtered(lambda c: c.website_id == website)[:1] or matching[:1]
            tiles.append({
                'name': category.with_context(lang=request.env.lang).name if category else label,
                'url': '/shop/category/%s' % request.env['ir.http']._slug(category)
                       if category else '/shop?' + urlencode({'search': search}),
                'image': '/web/image/product.public.category/%s/image_1024' % category.id
                         if category and category.image_128 else '/ar_pricecut_website/static/src/img/' + image,
            })
        return tiles

    @http.route('/pricecut-home', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kwargs):
        self._check_website()
        website = request.website
        Product = request.env['product.template']
        can_shop = website.has_ecommerce_access()
        products = Product.search(
            Domain(website.sale_product_domain()) & Domain('is_published', '=', True),
            order='website_sequence, name, id', limit=8,
        ) if can_shop else Product
        return request.render('ar_pricecut_website.homepage', {
            'products': products,
            'product_prices': products._get_sales_prices(website) if products else {},
            'departments': self._category_tiles() if can_shop else [],
            'can_shop': can_shop,
        })

    @http.route('/pricecut/about', type='http', auth='public', website=True, sitemap=True)
    def about(self, **kwargs):
        self._check_website()
        return request.render('ar_pricecut_website.about_page')

    @http.route('/pricecut/wholesale', type='http', auth='public', website=True, sitemap=True)
    def wholesale(self, **kwargs):
        self._check_website()
        return request.render('ar_pricecut_website.wholesale_page')

    @http.route('/pricecut/contact', type='http', auth='public', website=True, sitemap=True)
    def contact(self, **kwargs):
        self._check_website()
        return request.render('ar_pricecut_website.contact_page')
