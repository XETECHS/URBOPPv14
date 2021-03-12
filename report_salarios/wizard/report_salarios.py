# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2019 Xetechs, S.A.>.
#    (https://wwww.xetechs.com)
#    Author: Luis Aquino --> laquino@xetechs.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
##############################################################################

from odoo import fields, models, api


class wizard_salarios(models.TransientModel):
    _name = "wizard.salarios"

    periodo_id = fields.Many2one('hr.periodo', 'Periodo', required=True)
    company_id = fields.Many2one('res.company', 'Empresa', required=True, default=lambda self: self.env.user.company_id)
    empleados_ids = fields.Many2many('hr.employee', 'empleado_wizard_rel', 'wizard_id', 'empleado_id', 'Empleados')

    def create_report(self):
        context = self._context
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_salarios.template_reporte_libro_de_salarios',
            'datas': {
                'model': 'hr.payslip.run',
                'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                'ids': context.get('active_ids') and context.get('active_ids') or [],
                'periodo_id': self.periodo_id.id,
                'company_id': self.company_id.id,
                'empleados_ids': self.empleados_ids.ids,
            },
            'nodestroy': False

        }
        
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.salarios',
            'form': data,
        }
        return self.env.ref('report_salarios.action_reporte_libro_de_salarios').with_context(landscape=True).report_action(self, data=datas)