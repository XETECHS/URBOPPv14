# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    _inherit = "hr.contract"

    bonification_amount = fields.Monetary('Bonificacion Incentivo', required=True, tracking=True, help="Bonficiacion Incentivo")
    extra_bonification_amount = fields.Monetary('Bonificaciones Extra', required=True, tracking=True, help="Bonficiacion adicionales a la ley")
    extra_amount = fields.Monetary('Otros Incentivos', required=True, tracking=True, help="Otros incentivos")
    total_wage = fields.Monetary('Salario Total', compute="_compute_wage")

    @api.depends('wage', 'bonification_amount', 'extra_bonification_amount', 'extra_amount')
    def _compute_wage(self):
        total_wage = 0.00
        for rec in self:
            total_wage = (rec.wage + rec.bonification_amount + rec.extra_bonification_amount + rec.extra_amount)
            rec.update({
                'total_wage': total_wage or 0.00,
            })

HrContract()