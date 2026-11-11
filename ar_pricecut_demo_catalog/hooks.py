import base64
import json

from odoo import Command
from odoo.exceptions import UserError
from odoo.tools import file_open

CATEGORIES = (
    ('pantry', 'Groceries & Pantry', 'cat_pantry_hd.webp'),
    ('beverages', 'Beverages', 'cat_beverages_hd.webp'),
    ('beer', 'Beer & Stout', 'cat_beverages_hd.webp'),
    ('snacks', 'Snacks & Sweets', 'cat_snacks_hd.webp'),
    ('personal', 'Personal Care', 'cat_personal_hd.webp'),
    ('household', 'Household', 'cat_household_hd.webp'),
)
MODULE = 'ar_pricecut_demo_catalog'


def _owned(env, name, model, values):
    """Stable XML IDs make seeding repeatable and prevent duplicate sample records."""
    record = env.ref(f'{MODULE}.{name}', raise_if_not_found=False)
    if record:
        return record
    record = env[model].create(values)
    env['ir.model.data'].create({
        'module': MODULE, 'name': name, 'model': model,
        'res_id': record.id, 'noupdate': True,
    })
    return record


def post_init_hook(env):
    sites = env['website'].search([('pricecut_enabled', '=', True)])
    if len(sites) != 1:
        raise UserError('Enable Pricecut branding on exactly one website before installing the sample catalogue.')
    site = sites[0]
    if site.company_id.currency_id.name != 'TTD':
        raise UserError('These sample prices are in TTD. Set the intended company currency to TTD before installing this optional catalogue. No accounting settings are changed by this module.')
    env = env(context=dict(env.context, allowed_company_ids=[site.company_id.id]))
    site = env['website'].browse(site.id)
    website_categories, pos_categories = {}, {}
    for index, (key, name, filename) in enumerate(CATEGORIES):
        with file_open('ar_pricecut_website/static/src/img/' + filename, 'rb') as image:
            photo = base64.b64encode(image.read())
        # Reuse an existing exact category rather than duplicate a live catalogue.
        website_category = env['product.public.category'].search([
            ('name', '=', name), ('website_id', '=', site.id), ('parent_id', '=', False),
        ], limit=1)
        if not website_category:
            website_category = _owned(env, f'web_category_{key}', 'product.public.category', {
                'name': name, 'website_id': site.id, 'sequence': (index + 1) * 10,
                'image_1920': photo,
            })
        pos_category = env['pos.category'].search([('name', '=', name), ('parent_id', '=', False)], limit=1)
        if not pos_category:
            pos_category = _owned(env, f'pos_category_{key}', 'pos.category', {
                'name': name, 'sequence': (index + 1) * 10, 'image_512': photo,
            })
        website_categories[key] = website_category
        pos_categories[key] = pos_category
    with file_open(MODULE + '/data/products.json', 'r') as source:
        products = json.load(source)
    for index, item in enumerate(products):
        with file_open(MODULE + '/static/src/img/' + item['image'], 'rb') as image:
            photo = base64.b64encode(image.read())
        _owned(env, 'product_' + item['key'], 'product.template', {
            'name': item['name'],
            'default_code': 'AR-' + item['key'].upper().replace('_', '-'),
            'type': 'consu',
            'is_storable': False,
            'sale_ok': True,
            'purchase_ok': True,
            'available_in_pos': True,
            'company_id': site.company_id.id,
            'website_id': site.id,
            'is_published': True,
            'list_price': item['price'],
            'website_sequence': (index + 1) * 10,
            'public_categ_ids': [Command.set(website_categories[item['category']].ids)],
            'pos_categ_ids': [Command.set(pos_categories[item['category']].ids)],
            'image_1920': photo,
            'taxes_id': [Command.clear()],
            'supplier_taxes_id': [Command.clear()],
            'description': 'Spxcorp sample catalogue. Illustrative TTD price, not a verified A&R selling price. Review price, taxes, stock tracking, packaging and barcode before live trading. Image source: ' + item['source'],
        })
