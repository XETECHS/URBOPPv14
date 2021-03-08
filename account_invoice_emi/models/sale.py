# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.depends('state', 'order_line.invoice_status', 'account_invoice_emi_id.state')
    def _get_invoice_status(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.
        """
        unconfirmed_orders = self.filtered(lambda so: so.state not in ['sale', 'done'])
        unconfirmed_orders.invoice_status = 'no'
        confirmed_orders = self - unconfirmed_orders
        if not confirmed_orders:
            return
        line_invoice_status_all = [
            (d['order_id'][0], d['invoice_status'])
            for d in self.env['sale.order.line'].read_group([
                    ('order_id', 'in', confirmed_orders.ids),
                    ('is_downpayment', '=', False),
                    ('display_type', '=', False),
                ],
                ['order_id', 'invoice_status'],
                ['order_id', 'invoice_status'], lazy=False)]
        for order in confirmed_orders:
            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]
            if order.account_invoice_emi_id.state in ('confirm', 'to_approved', 'approved'):
                order.invoice_status = 'emi'
                #order.state = 'emi'
            elif order.account_invoice_emi_id.state == 'done':
                order.invoice_status = 'invoiced'
                #order.state = 'invoiced'
            else:
                if order.state not in ('sale', 'done'):
                    order.invoice_status = 'no'
                    order.state = 'paid'
                elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                    order.invoice_status = 'to invoice'
                elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                    order.invoice_status = 'invoiced'
                    #order.state = 'invoiced'
                elif line_invoice_status and all(invoice_status in ('invoiced', 'upselling') for invoice_status in line_invoice_status):
                    order.invoice_status = 'upselling'
                else:
                    order.invoice_status = 'no'
                    #order.state = 'paid'


    emi_paid = fields.Integer("invoiced", related="account_invoice_emi_id.paid_total", readonly=True)
    emi_unpaid = fields.Integer("Total EMI", related="account_invoice_emi_id.total_emi", readonly=True)
    is_emi_created = fields.Boolean(string="EMI done?", readonly=True, default=False)
    account_invoice_emi_id = fields.Many2one('account.invoice.emi', string="Account Invoice EMI")
    invoice_status = fields.Selection(selection_add=[ ('emi', 'Open EMI') ])


    def action_invoice_emi(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.emi',
            'res_id': self.account_invoice_emi_id.id,
            'views': [[False, "form"]],
        }
        
    def action_create_emi(self):
        if not self.account_invoice_emi_id:
            context = {'default_so_id': self.id,
                       'default_active': True}
            return {
                    'name': _('Account Invoice EMI'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice.emi',
                    'view_id': self.env.ref('account_invoice_emi.view_account_invoice_emi_form').id,
                    'type': 'ir.actions.act_window',
                    'context': context,
                    }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.emi',
            'res_id': self.account_invoice_emi_id.id,
            'views': [[False, "form"]],
        } 
            

    # @api.model
    # def create(self, vals):
    #     res = super(SaleOrder, self).create(vals)
    #     res.is_emi_created = False
    #     return res
