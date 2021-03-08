# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    
    def _account_invoice_emi_total(self):
        if not self.ids:
            self.total_account_invoice_emi = 0.0
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        account_invoice_emi = self.env['account.invoice.emi'].search([('so_id.partner_id', 'in', all_partner_ids), ('state', '!=', 'draft')])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_account_invoice_emi = len(account_invoice_emi)

    total_account_invoice_emi = fields.Integer(compute='_account_invoice_emi_total', string="Total EMI")