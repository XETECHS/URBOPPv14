# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

AREA = [
    ('31', '31.60'),
    ('47', '47.40'),
    ('63', '63.20'),
    ('79', '79.00'),
]

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tower = fields.Char(string='Tower')
    view = fields.Char(string='View')
    aream2 = fields.Selection(AREA, string="Area m2")

    