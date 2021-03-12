# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class HrEmploymentBenefitsConfig(models.Model):
    _name = "hr.employment.benefits.config"
    _description = "HR Employment Benefits Configurations"

    name = fields.Text('Prestacion', required=True)
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'hr_benefits_rules_rel', 'benefits_id', 'rule_id', string='Reglas salariales', copy=False, readonly=False, required=False)
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Regla Salarial', required=False)
    type = fields.Selection([
        ('bono_14', 'Bono 14'),
        ('vacaciones', 'Vacaciones'),
        ('aguinaldo', 'Aguinaldo'),
        ('indemnizacion', 'Indemnización')], 'Tipo prestacion', required=True)
    specific_date = fields.Boolean('¿Fecha especifica?', required=False, default=False)
    is_close = fields.Boolean('Liquidacion', default=False)
    specific_number_days = fields.Boolean('¿Numero de Dias especificos?', required=False, default=False)
    number_days = fields.Integer('Numero de Dias', required=False, default=1)
    day_from = fields.Integer('Dia Inicio', required=False)
    day_to = fields.Integer('Dia Fin', required=False)
    month_from = fields.Selection([
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre')], 'Mes Inicio', required=False, default="1")
    month_to = fields.Selection([
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre')], 'Mes Fin', required=False, default="1")
    company_id = fields.Many2one('res.company', string='Empresa', readonly=True, copy=False, required=True, default=lambda self: self.env.company)

HrEmploymentBenefitsConfig()


class HrEmploymentBenefits(models.Model):
    _name = 'hr.employment.benefits'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'HR Employment Benefits'

    name = fields.Char(string='Nombre', readonly=True, states={'draft': [('readonly', False)]})
    number = fields.Char(string='Correlativo', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='Desde', readonly=True, required=True, default=lambda self: fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Hasta', readonly=True, required=True, default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Empresa', readonly=True, copy=False, required=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('verify', 'Verificado'),
        ('done', 'Completado'),
        ('cancel', 'Anulado'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    company_id = fields.Many2one('res.company', string='Compañia', readonly=True, copy=False, default=lambda self: self.env['res.company']._company_default_get(), states={'draft': [('readonly', False)]})
    note = fields.Text(string='Notas', readonly=True, states={'draft': [('readonly', False)]})
    contract_id = fields.Many2one('hr.contract', string='Contrato', readonly=True, states={'draft': [('readonly', False)]})
    number_days = fields.Integer('Total dias', compute="_compute_days", store=True)
    provision_ids = fields.One2many('hr.employment.benefits.provision', 'benefits_id', 'Provisiones')
    line_ids = fields.One2many('hr.employment.benefits.lines', 'slip_id', 'Calculo')
    salaries_ids = fields.One2many('hr.employment.benefits.salaries', 'slip_id', 'Salarios')
    is_manual_wage = fields.Boolean('¿Salario Manual?', required=False, default=False)
    is_average_wage = fields.Boolean('¿Salario promedio?', required=False, default=False)
    wage = fields.Float('Salario')
    average_wage = fields.Float('Salario promedio', compute="_compute_salaries")
    journal_id = fields.Many2one('account.journal', ' Diario', required=True)
    move_id = fields.Many2one('account.move', 'Asiento Contable', required=False)
    date_account = fields.Date('Fecha contable', required=False)
    config_ids = fields.Many2many('hr.employment.benefits.config', 'hr_benefits_config_rel', 'benefits_id', 'config_id', string='Prestacion', copy=False, readonly=False, required=True)


    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for rec in self:
            delta = rec.date_to - rec.date_from
            rec.number_days = delta.days

    @api.depends('is_average_wage', 'salaries_ids')
    def _compute_salaries(self):
        amount_salaries = 0.00
        for rec in self:
            for line in rec.salaries_ids:
                amount_salaries += line.total
            lines_number = len(rec.salaries_ids.ids) or 1.00
            rec.write({
                'average_wage': (amount_salaries / lines_number) or 0.00
            })

    def last_day_of_month(self, any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        return next_month - datetime.timedelta(days=next_month.day)

    def monthlist(self, begin, end):
        begin = datetime.strptime(begin, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")

        result = []
        while True:
            if begin.month == 12:
                next_month = begin.replace(year=begin.year+1,month=1, day=1)
            else:
                next_month = begin.replace(month=begin.month+1, day=1)
            if next_month > end:
                break
            result.append ([begin.strftime("%Y-%m-%d"), self.last_day_of_month(begin).strftime("%Y-%m-%d")])
            begin = next_month
        result.append ([begin.strftime("%Y-%m-%d"),end.strftime("%Y-%m-%d")])
        return result

    @api.onchange('contract_id')
    def onchange_contract(self):
        for rec in self:
            if rec.contract_id:
                rec.date_from = rec.contract_id.date_start
    
    @api.onchange('is_manual_wage')
    def onchange_wage(self):
        for rec in self:
            if rec.contract_id:
                rec.wage = rec.contract_id.wage
    
    def action_caculate(self):
        days_year = 365.00
        amount = 0.00
        sequence = 0
        for rec in self:
            if rec.is_average_wage:
                self.compute_salaries()
                if rec.is_average_wage == True and rec.average_wage == 0.00:
                    raise UserError(('No se puede procesa porque tiene Salario Promedio de Q. 0.00'))
                if rec.config_ids:
                    for conf in rec.config_ids:
                        #amount = 0.00
                        sequence += 1
                        if conf.type == 'indemnizacion':
                            amount = (rec.number_days * rec.average_wage / days_year)
                        elif conf.type == 'bono_14':
                            amount = (192 * rec.average_wage / days_year)
                        elif conf.type == 'aguinaldo':
                            amount = (205 * rec.average_wage / days_year)
                        elif conf.type == 'vacaciones':
                            amount = (conf.number_days * rec.average_wage / days_year)
                        res = {
                            'slip_id': rec.id,
                            'salary_rule_id': conf.salary_rule_id.id,
                            'name': conf.name,
                            'note': conf.name,
                            'sequence': sequence,
                            'quantity': 1.00,
                            'rate': 100.00,
                            'amount': amount,
                            }
                        self.env['hr.employment.benefits.lines'].create(res)
            elif rec.is_manual_wage:
                #self.compute_salaries()
                if rec.is_manual_wage == True and rec.wage == 0.00:
                    raise UserError(('No se puede procesa porque tiene Salario base de Q. 0.00'))
                if rec.config_ids:
                    for conf in rec.config_ids:
                        #amount = 0.00
                        sequence += 1
                        if conf.type == 'indemnizacion':
                            amount = (rec.number_days * rec.wage / days_year)
                        elif conf.type == 'bono_14':
                            amount = (192 * rec.wage / days_year)
                        elif conf.type == 'aguinaldo':
                            amount = (205 * rec.wage / days_year)
                        elif conf.type == 'vacaciones':
                            amount = (conf.number_days * rec.wage / days_year)
                        res = {
                            'slip_id': rec.id,
                            'salary_rule_id': conf.salary_rule_id.id,
                            'name': conf.name,
                            'note': conf.name,
                            'sequence': sequence,
                            'quantity': 1.00,
                            'rate': 100.00,
                            'amount': amount,
                            }
                        self.env['hr.employment.benefits.lines'].create(res)
            rec.write({
                'state': 'verify',
            })
        return True
    
    def compute_salaries(self):
        salaries_obj = self.env['hr.employment.benefits.salaries']
        payslip_line_obj = self.env['hr.payslip.line']
        lines = []
        for rec in self:
            lines_ids = payslip_line_obj.search([('employee_id', '=', rec.employee_id.id), ('contract_id', '=', rec.contract_id.id)], order="id desc", limit=10)
            for line in lines_ids:
                if line.salary_rule_id.code == 'BASIC' and line.slip_id.state == 'done':
                    res = {
                        'slip_id': rec.id,
                        'payslip_line_id': line.id,
                    }
                    #lines.append((1, rec.id, res))
                    salaries_obj.create(res)
            #rec.write({
            #    'salaries_ids': lines,
            #})
        return True

    def action_post(self):
        move_obj = self.env['account.move']
        lines = []
        move_id = False
        for rec in self:
            for line in rec.line_ids:
                debit = {
                    'account_id': line.salary_rule_id.account_debit.id,
                    'name': line.name,
                    'debit': line.total,
                }
                lines.append((0,0,debit))
                credit = {
                    'account_id': line.salary_rule_id.account_credit.id,
                    'name': line.name,
                    'credit': line.total,
                }
                lines.append((0,0,credit))
            if lines:
                move = {
                    'date': fields.Date.today(),
                    'journal_id': rec.journal_id.id,
                    'type': 'entry',
                    'ref': rec.name,
                    'state': 'draft',
                    'line_ids': lines,
                }
                move_id = move_obj.create(move)
                move_id.action_post()
            rec.write({
                'move_id': move_id.id,
                'state': 'done',
            })
        return True

    
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('hr.employment.benefits') or _('S/N')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.employment.benefits') or _('S/N')
        res = super(HrEmploymentBenefits, self).create(vals)
        return res

    def action_cancel(self):
        for rec in self:
            rec.move_id.button_draft()
            rec.move_id.button_cancel()
            rec.write({
                'state': 'cancel',
            })
        return True
HrEmploymentBenefits()

class HrEmploymentBenefitsLines(models.Model):
    _name = 'hr.employment.benefits.lines'
    _description = 'HR Employment Benefits Lines'

    name = fields.Char(required=True, translate=True)
    note = fields.Text(string='Descripción')
    code = fields.Char(string="Codigo", related="salary_rule_id.code")
    sequence = fields.Integer(required=True, index=True, default=5)
    slip_id = fields.Many2one('hr.employment.benefits', string='Pay Employment Benefits', required=True, ondelete='cascade')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Regla Salarial', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contrato', related="slip_id.contract_id", index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related="slip_id.employee_id", index=True)
    rate = fields.Float(string='Porcentaje (%)', digits='Payroll Rate', default=100.0)
    amount = fields.Float(string="Monto", digits='Payroll')
    quantity = fields.Float(string="Cantidad", digits='Payroll', default=1.0)
    total = fields.Float(compute='_compute_total', string='Total', digits='Payroll', store=True)
    date_from = fields.Date(string='Desde', related="slip_id.date_from", store=True)
    date_to = fields.Date(string='hasta', related="slip_id.date_to", store=True)
    company_id = fields.Many2one(related='slip_id.company_id')
    
    
    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100


HrEmploymentBenefitsLines()

class HrEmploymentBenefitsSalaries(models.Model):
    _name = 'hr.employment.benefits.salaries'
    _description = 'HR Employment Benefits Salaries'

    slip_id = fields.Many2one('hr.employment.benefits', string='Pay Employment Benefits', required=True, ondelete='cascade')
    payslip_line_id = fields.Many2one('hr.payslip.line', 'Salario', required=True)
    date_from = fields.Date('Del', related="payslip_line_id.date_from")
    date_to = fields.Date('Al', related="payslip_line_id.date_to")
    name = fields.Char('Descripcion', related="payslip_line_id.name")
    rate = fields.Float(string='Porcentaje (%)', related="payslip_line_id.rate")
    amount = fields.Float(string="Importe", related="payslip_line_id.amount")
    quantity = fields.Float(string="Cantidad", related="payslip_line_id.quantity")
    total = fields.Float(string="Total", related="payslip_line_id.total")

HrEmploymentBenefitsSalaries()
class HrEmploymentBenefitsProvision(models.Model):
    _name = 'hr.employment.benefits.provision'
    _description = 'HR Employment Benefits Provision'

    benefits_id = fields.Many2one('hr.employment.benefits', 'Employment Benefits', ondelete="cascade")
    rule_id = fields.Many2one('hr.salary.rule', 'Regla Salarial', required=False)
    name = fields.Text('Descripcion', required=True)
    amount_provision = fields.Float('Monto Provisionado', required=True)

    @api.onchange('rule_id')
    def onchange_rule(self):
        for rec in self:
            if rec.rule_id:
                rec.name = rec.rule_id.name

HrEmploymentBenefitsProvision()