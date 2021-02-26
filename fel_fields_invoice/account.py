# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'account.move'

    fel_serie = fields.Char(string='FEL Serie')
    fel_no = fields.Char(string='FEL Number')