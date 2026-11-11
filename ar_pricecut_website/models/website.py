import base64
import logging

from odoo import api, fields, models
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    pricecut_enabled = fields.Boolean('A&R Pricecut branding', default=False)
    pricecut_phone = fields.Char('Store phone', default='+1 (868) 324-3448')
    pricecut_address = fields.Char(
        'Store address', default='Eastern Main Road, Sangre Grande, Trinidad and Tobago')
    pricecut_hours = fields.Char(
        'Confirmed opening hours',
        help='Leave blank until confirmed. The old sign and online listing have different hours.')
    pricecut_setup_done = fields.Boolean(copy=False)
    pricecut_previous_homepage = fields.Char(copy=False)
    pricecut_previous_name = fields.Char(copy=False)
    pricecut_previous_logo = fields.Binary(copy=False, attachment=False)

    def _pricecut_phone_uri(self):
        self.ensure_one()
        return 'tel:' + ''.join(c for c in (self.pricecut_phone or '') if c.isdigit() or c == '+')

    @api.model
    def _pricecut_setup(self):
        """Initialize one unambiguous website; preserve future editor changes."""
        websites = self.search([])
        targets = websites.filtered(lambda w: w.pricecut_enabled or
            w.homepage_url == '/pricecut-home' or 'pricecut' in w.name.casefold())
        if not targets and len(websites) == 1:
            targets = websites
        if not targets:
            _logger.warning('Pricecut: select the target website, enable Pricecut branding, '
                            'then click Initialize Pricecut Website.')
        Menu = self.env['website.menu']
        for site in targets.filtered(lambda w: not w.pricecut_setup_done):
            with file_open('ar_pricecut_website/static/src/img/pricecut-logo.png', 'rb') as image:
                site.write({
                    'pricecut_previous_homepage': site.homepage_url,
                    'pricecut_previous_name': site.name,
                    'pricecut_previous_logo': site.logo,
                    'pricecut_enabled': True,
                    'homepage_url': '/pricecut-home',
                    'name': 'A&R Pricecut Supermarket',
                    'logo': base64.b64encode(image.read()),
                })
            if not site.menu_id:
                Menu.create({'name': 'Main Menu', 'website_id': site.id})
                site.invalidate_recordset(['menu_id'])
            if not site.menu_id:
                raise ValueError('Pricecut setup requires a website root menu.')
            existing = Menu.search([('website_id', '=', site.id), ('parent_id', '=', site.menu_id.id)])
            for name, url, aliases, seq in [
                ('Home', '/', ('/', '/pricecut-home'), 10),
                ('Shop', '/shop', ('/shop',), 20),
                ('Departments', '/pricecut-home#departments', (), 30),
                ('Wholesale', '/pricecut/wholesale', (), 40),
                ('About', '/pricecut/about', (), 50),
                ('Contact', '/pricecut/contact', ('/contactus',), 60),
            ]:
                match = existing.filtered(lambda m: m.url in (*aliases, url) or m.name.casefold() == name.casefold())[:1]
                if match:
                    match.write({'name': name, 'url': url, 'sequence': seq})
                else:
                    Menu.create({'name': name, 'url': url, 'sequence': seq,
                                 'website_id': site.id, 'parent_id': site.menu_id.id})
            site.pricecut_setup_done = True

    def action_pricecut_initialize(self):
        self.ensure_one()
        # Only website administrators may initialize branding; this method is RPC callable.
        self.check_access('write')
        self.pricecut_enabled = True
        self._pricecut_setup()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
