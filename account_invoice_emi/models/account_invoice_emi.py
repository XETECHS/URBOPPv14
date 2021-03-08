# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import models, fields, api, _


class Account_Invoice_EMI(models.Model):
    _name = "account.invoice.emi"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Account Invoice EMI"
    _order = 'id desc'

    @api.depends('so_id')
    def _compute_sales_order_amount(self):
        """
        Compute the amounts of the Sales Order line.
        """
        for line in self:
            down_amount = 0.0
            if line.so_id:
                for so_line in line.so_id.order_line:
                    if so_line.is_downpayment:
                        down_amount += so_line.price_unit
            line.update({
                'so_amount': line.so_id.amount_total - down_amount,
                'so_untax_amount': line.so_id.amount_total - line.so_id.amount_tax - down_amount,
                'so_tax_amount': line.so_id.amount_tax
            })

    @api.depends('so_id.invoice_ids', 'inv_emi_lines.state', 'state')
    def get_total_invoice(self):
        for res in self:
            res.total_invoice = len(res.so_id.mapped('invoice_ids'))
            res.emi_amount = round(sum([x.inv_amount for x in res.inv_emi_lines]), 2)
            res.interest_amount = round(sum([x.interest_amount for x in res.inv_emi_lines]), 2)
            res.total_amount = res.emi_amount + res.interest_amount

    
    name = fields.Char(string='EMI Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), track_visibility='always')
    title = fields.Char(string='Title EMI', required=False, readonly=False)
    so_id = fields.Many2one('sale.order', string="Sales Order", required=True, domain="[('state', '=', 'done')]", track_visibility='onchange')
    type = fields.Selection([('fixed', 'Fixed'), ('manual', 'Manual')], string="EMI Type", default="manual",
                            track_visibility='onchange')
    total = fields.Integer(string="Total EMI", track_visibility='onchange', default=1)
    total_emi = fields.Integer(string="Total EMI", readonly=True, track_visibility='onchange', compute="_compute_emi_invoices")
    paid_total = fields.Integer(string="Invoiced EMI", readonly=True, compute="_compute_emi_invoices")
    interest = fields.Float(string="Interest Rate", track_visibility='onchange')
    inv_emi_lines = fields.One2many('account.invoice.emi.line', 'acc_inv_emi_id', string="EMI Lines")
    currency_id = fields.Many2one(related="so_id.currency_id", string="Currency", readonly=True, required=True)
    so_untax_amount = fields.Monetary(compute='_compute_sales_order_amount', string='Untax Amount', readonly=True, store=True)
    so_tax_amount = fields.Monetary(compute='_compute_sales_order_amount', string='Tax Amount', readonly=True, store=True)
    so_amount = fields.Monetary(compute='_compute_sales_order_amount', string='SO Amount', readonly=True, store=True)

    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('to_approved', 'To Be Approved'),
            ('approved', 'Approved'),
            ('done', 'Done'),
            ('reject', 'Reject')
        ], string="State", default="draft", select=True, readonly=True, copy=False, track_visibility='always')
    partner_id = fields.Many2one(related="so_id.partner_id", string='Customer', store=True)
    project_id = fields.Many2one("project.project", string='Project Name', track_visibility='onchange')
    total_invoice = fields.Integer(string="Total Invoice", compute="get_total_invoice", track_visibility='onchange')
    emi_amount = fields.Monetary(string="EMI Amount", compute="get_total_invoice", store=True, track_visibility='onchange')
    interest_amount = fields.Monetary(string="EMI Interest", compute="get_total_invoice", store=True, track_visibility='onchange')
    total_amount = fields.Monetary(string="Total Amount", compute="get_total_invoice", store=True, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string="Invoice Journal", track_visibility='onchange')
    start_date = fields.Date(string="Start Date", track_visibility='onchange')
    emi_tax_ids = fields.Many2many('account.tax', 'emi_line_tax', 'emi_line_id', 'tax_id', string='Taxes',
                                   domain=[('type_tax_use', '!=', 'none'), '|', ('active', '=', False), ('active', '=', True)],
                                   default=[2])
    inv_description = fields.Char(string="Invoice Description", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          help="The analytic account related to a sales order.")


    @api.depends('inv_emi_lines')
    def _compute_emi_invoices(self):
        invoiced = 0
        #lines = 0
        for rec in self:
            #if rec.inv_emi_lines:
            for line in rec.inv_emi_lines:
                if line.state == 'invoiced':
                    invoiced += 1
            rec.update({
                'total_emi': len(rec.inv_emi_lines.ids) or 0,
                'paid_total': invoiced or 0,
            })


    @api.onchange('interest')
    def onchange_total_interest(self):
        for res in self:
            if res.interest < 0 and res.interest > 100:
                raise ValidationError(_("Interest must be positive value and lessthen 100"))

    @api.onchange('total')
    def onchange_total_total(self):
        for res in self:
            if res.type == 'fixed':
                if res.total <= 0:
                    raise ValidationError(_("Total Invoice must be > 0"))

    @api.onchange('type')
    def onchange_type(self):
        for res in self:
            if res.type:
                res.total = 0
                res.interest = 0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('account.invoice.emi') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('account.invoice.emi') or _('New')
        result = super(Account_Invoice_EMI, self).create(vals)
        result.partner_id = result.so_id.partner_id.id
        result.currency_id = result.so_id.currency_id.id

        return result

        # @api.multi

    def write(self, values):
        analytic_account_id = values['analytic_account_id'] if 'analytic_account_id' in values \
            else self.analytic_account_id
        inv_description = values['inv_description'] if 'inv_description' in values else self.inv_description
        for line in self.inv_emi_lines:
            line.update({'inv_description': inv_description, 'analytic_account_id': analytic_account_id})
        res = super(Account_Invoice_EMI, self).write(values)
        return res

    ##@api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = rec.so_id.name + '-' + rec.name
            result.append((rec.id, name))
        return result

    def action_confirm(self):
        if not self.so_id:
            raise ValidationError(_("Please select sales order"))
        self._compute_sales_order_amount()
        if self.search([('so_id', '=', self.so_id.id), ('state', '=', 'confirm'), ('id', '!=', self.id)]):
            raise ValidationError(_("You can't confirm the Account invoice EMI record because same sales order selected confirm record exists."))
        if self.type == 'fixed':
            self.make_emi_generate()
        #self.total_emi = len(self.inv_emi_lines.ids)
        if len(self.inv_emi_lines) == 0:
            raise ValidationError(_("Please create some EMI"))
        total = sum(rec.inv_amount for rec in self.inv_emi_lines)
        self.partner_id = self.so_id.partner_id.id
        #if round(total, 2) != self.so_amount:
        #    raise ValidationError(_("Total amount of  EMI amount must be Equal to sale order amount"))
        self.so_id.write({'emi_unpaid': len(self.inv_emi_lines.ids),
                          'is_emi_created': True,
                          'account_invoice_emi_id': self.id})
        return self.write({'state': 'confirm'})

    ##@api.multi
    def make_emi_generate_old(self):
        self._cr.execute("DELETE FROM account_invoice_emi_line WHERE acc_inv_emi_id=%s""" % self.id)
        if self.total <= 0:
                raise ValidationError(_("Total Invoice must be > 0"))
        invoice = self.so_amount / self.total
        interest = (invoice * self.interest)/100
        line_data = self.inv_emi_lines
        date = self.start_date
        item = 0
        for t in range(self.total):
            item += 1
            if item > self.total:
                break
            line = line_data.new()
            line.acc_inv_emi_id = self.id
            line.sequence = t + 1
            line.date = date
            line.inv_amount = invoice
            line.interest_amount = interest
            line.total = interest + invoice
            line.state = 'draft'
            line.currency_id = self.currency_id.id
            self.inv_emi_lines = self.inv_emi_lines | line
            date = date + relativedelta(months=1)
    
    def make_emi_generate(self):
        emi_line_obj = self.env['account.invoice.emi.line']
        self._cr.execute("DELETE FROM account_invoice_emi_line WHERE acc_inv_emi_id=%s""" % self.id)
        if self.total <= 0:
                raise ValidationError(_("Total Invoice must be > 0"))
        date = self.start_date
        items = int(self.total)
        for line in range(items):
            res = {
                'sequence': line,
                'acc_inv_emi_id': self.id,
                'date': date,
                'inv_amount': (self.so_amount / self.total),
                'interest_amount': ((self.so_amount * self.interest)/100),
                'state': 'draft',
                'currency_id': self.currency_id.id,
                }
            emi_line_obj.create(res)
            date = date + relativedelta(months=1)

    ##@api.multi
    def action_to_be_approved(self):
        if self.so_id:
            self._compute_sales_order_amount()
        # if self.type == 'fixed':
        #     self.make_emi_generate()
        #self.total_emi = len(self.inv_emi_lines.ids)
        if len(self.inv_emi_lines) == 0:
            raise ValidationError(_("Please create some EMI"))
        total = sum(rec.inv_amount for rec in self.inv_emi_lines)
        self.partner_id = self.so_id.partner_id.id
        #if round(total, 2) != self.so_amount:
        #    raise ValidationError(_("Total amount of  EMI amount must be Equal to sale order amount"))
        return self.write({'state': 'to_approved'})

    #@api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    #@api.multi
    def action_reject(self):
        return self.write({'state': 'reject'})

    #@api.multi
    def action_approved(self):
        for res in self.inv_emi_lines:
            res.state = 'to_invoice'
        return self.write({'state': 'approved'})

    #@api.multi
    def action_done(self):
        if not all([x.state == 'invoiced' for x in self.inv_emi_lines]):
            raise ValidationError(_("You can not set done, some EMI need to create invoice panding"))
        return self.write({'state': 'done'})

    #@api.multi
    def action_view_invoice(self):
        invoices = [x.invoice_id.id for x in self.inv_emi_lines]
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class Account_Invoice_EMI_Line(models.Model):
    _name = "account.invoice.emi.line"

    @api.depends('inv_amount', 'acc_inv_emi_id')
    def _compute_amount(self):
        """
        Compute the amounts of the EMI line.
        """
        for line in self:
            interest_amount = (line.inv_amount * line.acc_inv_emi_id.interest) / 100.0
            line.update({
                'interest_amount': interest_amount,
                'total': interest_amount + line.inv_amount,
            })
    name = fields.Char(string="Number")
    acc_inv_emi_id = fields.Many2one('account.invoice.emi', string="Invoice EMI")
    sequence = fields.Integer(string="No.")
    date = fields.Date(string="Date")
    inv_amount = fields.Monetary(string="Invoice Amount")
    interest_amount = fields.Monetary(compute='_compute_amount', string="Interest Amount", readonly=True, store=True)
    total = fields.Monetary(compute='_compute_amount', string="Total", readonly=True, store=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('to_invoice', 'To Invoice'),
            ('invoiced', 'Invoiced'),
        ], string="State", default="draft")
    partner_id = fields.Many2one(related="acc_inv_emi_id.partner_id", string='Customer', store=True)
    invoice_id = fields.Many2one('account.move', string="Invoice#", store=True)
    sale_order_id = fields.Many2one(related="acc_inv_emi_id.so_id", string="Sale Order", store=True)
    project_id = fields.Many2one(related="acc_inv_emi_id.project_id", string="Project", store=True)
    inv_status = fields.Selection(related="invoice_id.state", string="Invoice Status", store=True)
    inv_description = fields.Char(string="Invoice Description")
    currency_id = fields.Many2one(related="acc_inv_emi_id.currency_id", string="Currency", readonly=True, required=True, store=False)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.")

    #@api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.acc_inv_emi_id.name) + '-' + str(rec.sequence)
            result.append((rec.id, name))
        return result

    #@api.multi
    def create_invoice(self):
        product_data = self.env.ref('account_invoice_emi.service_payment_product_emi')
        for order in self.acc_inv_emi_id.so_id:
            order.emi_paid += 1
            amount = self.inv_amount + self.interest_amount
            if product_data.invoice_policy != 'order':
                raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
            if product_data.type != 'service':
                raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
            if self.acc_inv_emi_id.emi_tax_ids:
                tax_ids = self.acc_inv_emi_id.emi_tax_ids.ids
            else:
                taxes = product_data.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes, product_data, order.partner_shipping_id).ids
                else:
                    tax_ids = taxes.ids
            context = {'lang': order.partner_id.lang}
            analytic_tag_ids = []
            for line in order.order_line:
                analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
            del context
            inv_obj = self.env['account.move']
            ir_property_obj = self.env['ir.property']

            account_id = False
            if product_data.id:
                account_id = order.fiscal_position_id.map_account(product_data.property_account_income_id or product_data.categ_id.property_account_income_categ_id).id
            if not account_id:
                inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
            if not account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                    (self.product_id.name,))

            if self.inv_amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))
            # context = {'lang': order.partner_id.lang}
            if self.acc_inv_emi_id.inv_description:
                name = _('%s : EMI %s / %s') % (self.acc_inv_emi_id.inv_description, order.emi_paid, order.emi_unpaid)
            elif self.acc_inv_emi_id.project_id:
                name = _('%s : EMI %s / %s') % (self.acc_inv_emi_id.project_id.name, order.emi_paid, order.emi_unpaid)
            else:
                name = _('%s : EMI %s / %s') % (product_data.name, order.emi_paid, order.emi_unpaid)
            invoice = inv_obj.create({
                'name': "/",
                'invoice_origin': order.name,
                'move_type': 'out_invoice',
                'partner_id': order.partner_invoice_id.id,
                'narration': '',
                'invoice_line_ids': [(0, 0, {
                    'name': name,
                    #'origin': order.name,
                    'account_id': account_id,
                    'price_unit': amount,
                    'quantity': 1.0,
                    'discount': 0.0,
                    'product_uom_id': product_data.uom_id.id,
                    'product_id': product_data.id,
                    'analytic_account_id': self.analytic_account_id.id or False,
                    'tax_ids': [(6, 0, tax_ids)],
                    #'account_analytic_id': order.account_analytic_id.id or False,
                })],
                'currency_id': order.currency_id.id,
                'invoice_payment_term_id': order.payment_term_id.id,
                'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
                'team_id': order.team_id.id,
                'user_id': order.user_id.id,
                'journal_id': self.acc_inv_emi_id.journal_id and self.acc_inv_emi_id.journal_id.id or False
                })
            #invoice._recompute_tax_lines()
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice, 'origin': order},
                                           subtype_id=self.env.ref('mail.mt_note').id)
            self.invoice_id = invoice.id
            self.state = 'invoiced'
            #self.acc_inv_emi_id.paid_total += 1
        if self._context.get('open_invoices', False):
            return self.acc_inv_emi_id.so_id.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def auto_create_invoice_emi(self):
        current_date = fields.Date.context_today(self)
        for account_inv_emi in self.search([('date', '=', current_date), ('state', '=', 'draft')]):
            account_inv_emi.create_invoice()
        return True

    @api.model
    def create(self, vals):
        res = super(Account_Invoice_EMI_Line, self).create(vals)
        if res.acc_inv_emi_id.inv_description:
            res.inv_description = res.acc_inv_emi_id.inv_description
        if res.acc_inv_emi_id.analytic_account_id:
            res.analytic_account_id = res.acc_inv_emi_id.analytic_account_id
        if res.acc_inv_emi_id.type != 'fix':
            old_recoreds = self.env['account.invoice.emi.line'].search([('acc_inv_emi_id', '=', res.acc_inv_emi_id.id), ('id', '!=', res.id)])
            res.sequence = len(old_recoreds) + 1
        # msg = "%s EMI Created with Amount %s with (Invoice amount %s and Interest %s)" % (res.sequence, res.total, res.inv_amount, res.interest_amount)
        # res.acc_inv_emi_id.message_post(body=_('<a href=# data-oe-model=account.invoice.emi data-oe-id=%d>%s</a>') % (res.id, msg))
        return res

    # @api.multi
    def write(self, values):
        res = super(Account_Invoice_EMI_Line, self).write(values)
        if 'state' in values:
            msg = "#%s EMI Invoice Created with Amount %s with (Invoice amount %s and Interest %s) on %s" % (self.sequence, self.total, self.inv_amount, self.interest_amount, fields.Date.today())
            self.acc_inv_emi_id.message_post(body=_('<a href=# data-oe-model=account.invoice.emi data-oe-id=%d>%s</a>') % (self.id, msg))
        return res

    #@api.multi
    def action_view_invoice(self):
        if self.invoice_id:
            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.invoice_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
