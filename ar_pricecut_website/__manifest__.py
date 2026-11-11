{
    'name': 'A&R Pricecut Supermarket Website',
    'version': '19.0.1.0.0',
    'summary': 'Sangre Grande supermarket website with native Odoo eCommerce',
    'category': 'Website',
    'author': 'Spxcorp Limited',
    'license': 'LGPL-3',
    'depends': ['website_sale'],
    'data': ['views/templates.xml', 'views/website_views.xml', 'data/setup.xml'],
    'assets': {
        'web.assets_frontend': [
            'ar_pricecut_website/static/src/css/pricecut.css',
            'ar_pricecut_website/static/src/js/pricecut.js',
        ],
    },
    'installable': True,
    'application': True,
}
