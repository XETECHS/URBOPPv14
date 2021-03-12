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

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import models, fields


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'

    is_ingreso = fields.Boolean('Es Ingreso?', required=False, default=False)
    is_descuento = fields.Boolean('Es Descuento?', required=False, default=False)
    is_prestacion = fields.Boolean('Es Prestacion?', required=False, default=False)
    tipo_ingreso = fields.Selection([
        ('base', 'Salario Base'),
        ('extras', 'Horas Extras'),
        ('qty_he', 'Cantidad Hora Extra'),
        ('valor_he', 'Valor Horas Extras'),
        ('bonificacion', 'Bonificacion Decreto'),
        ('incentivos', 'Bonificaciones Incentivos'),
        ('bono_horas', 'Bonificacion por Horas'),
        ('bono_resultados', 'Bonificacion por Resultados'),
        ('otras_bonificacion', 'Otras bonificaciones'),
        ('comisiones', 'Comisiones'),
        ('otros_ingresos', 'Otros Ingresos')], 'Ingresos', required=False,
        help="Tipo de columna a la que pertenece dentro del reporte impreso")
    tipo_descuento = fields.Selection([
        ('igss', 'IGSS Laboral'),
        ('isr', 'ISR'),
        ('anticipo1', 'Descuento 1'),
        ('anticipo2', 'Descuento 2'),
        ('anticipo3', 'Descuento 3'),
        ('otros_anticipos', 'Descuento 4'),
        ('prestamo', 'Seguro'),
        ('alimentos', 'Anticipo S/Sueldo'),
        ('otros_descuentos', 'Otros Descuentos')], 'Descuentos/Deducciones', required=False,
        help="Tipo de columna a la que pertenece dentro del reporte impreso")
    prestaciones = fields.Selection([
        ('bono_14', 'Bono 14'),
        ('aguinaldo', 'Aguinaldo'),
        ('vacaciones', 'Vacaciones'),
        ('indemnizacion', 'Indemnizacion'),
        ('igss_patronal', 'IGSS Patronal'),
        ('otra_prestacion', 'Otras Prestaciones')], 'Prestaciones', required=False, help="Tipo de prestacion")


class hr_periodo(models.Model):
    _name = "hr.periodo"
    _description = "Periodos de pagos"

    name = fields.Char('Periodo', required=True)
    from_date = fields.Date('Desde', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    to_date = fields.Date('Hasta', required=True, default=lambda *a: str(
        datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
