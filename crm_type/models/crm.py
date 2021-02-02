from odoo import api, models, fields

TYPE = [
('CETUS', 'CETUS'),
('CETI', 'CETI'),
('DELTA', 'DELTA'),
('TAU', 'TAU'),
('KAI', 'KAI'),
('MENKAR', 'MENKAR'),
('IPSILON','IPSILON'),
]


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    type_crm = fields.Selection(TYPE, string='Tipo')
