# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

APARTMENT = [
('CETUS', 'CETUS'),
('CETI', 'CETI'),
('DELTA', 'DELTA'),
('TAU', 'TAU'),
('KAI', 'KAI'),
('MENKAR', 'MENKAR'),
]


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    apartment = fields.Selection(APARTMENT, string='Apartment')

    