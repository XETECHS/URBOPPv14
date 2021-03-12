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

from odoo import api, models,_
import time
import datetime


class SalariosReport(models.AbstractModel):
    _name = 'report.report_salarios.template_reporte_libro_de_salarios'

    def _get_report_data(self,data):
        # pool = pooler.get_pool(cr.dbname)
        payslip_obj = self.env['hr.payslip']
        periodo_obj = self.env['hr.periodo']
        empleado_obj = self.env['hr.employee']
        result = []
        linea = {}
        item = 0
        dias_trabajados = 0.00
        hr_ordinarias = 0.00
        # Ingresos
        base = 0.00
        extras = 0.00
        bonificacion = 0.00
        bono_horas = 0.00
        bono_resultados = 0.00
        valor_he = 0.00
        qty_he = 0.00
        incentivos = 0.00
        comisiones = 0.00
        otros_ingresos = 0.00
        # Deducciones
        igss = 0.00
        isr = 0.00
        anticipos1 = 0.00
        anticipos2 = 0.00
        anticipos3 = 0.00
        otros_anticipos = 0.00
        prestamo = 0.00
        alimentos = 0.00
        otros_descuentos = 0.00
        # Prestaciones
        bono14 = 0.00
        aguinaldo = 0.00
        vacaciones = 0.00
        indemnizacion = 0.00
        igss_patronal = 0.00
        otra_prestacion = 0.00
        empleados = data['form']['empleados_ids']
        periodo = data['form']['periodo_id']
        empresa = data['form']['company_id']
        periodo_id = periodo_obj.browse(periodo)
        payslip_ids = payslip_obj.search(
                                         [('company_id', '=', empresa[0]), ('date_to', '>=', periodo_id[0].from_date),
                                          ('date_to', '<=', periodo_id[0].to_date), ('state', '=', 'done'),
                                          ('employee_id', 'in', empleados)])
        # payslip_ids.sort()
        for line in payslip_ids:
            # Ingresos
            base = 0.00
            extras = 0.00
            bonificacion = 0.00
            bono_horas = 0.00
            bono_resultados = 0.00
            valor_he = 0.00
            qty_he = 0.00
            incentivos = 0.00
            comisiones = 0.00
            otros_ingresos = 0.00
            # Deducciones
            igss = 0.00
            isr = 0.00
            anticipos1 = 0.00
            anticipos2 = 0.00
            anticipos3 = 0.00
            otros_anticipos = 0.00
            prestamo = 0.00
            alimentos = 0.00
            otros_descuentos = 0.00
            # Prestaciones
            bono14 = 0.00
            aguinaldo = 0.00
            vacaciones = 0.00
            indemnizacion = 0.00
            igss_patronal = 0.00
            otra_prestacion = 0.00
            item += 1
            dias_trabajados = sum([x.number_of_days for x in line.worked_days_line_ids])
            hr_ordinarias = sum([x.number_of_hours for x in line.worked_days_line_ids])
            for l in line.details_by_salary_rule_category:
                if l.salary_rule_id.is_ingreso == True:
                    if l.salary_rule_id.tipo_ingreso == "base":
                        base += l.total
                    elif l.salary_rule_id.tipo_ingreso == "extras":
                        extras += l.total
                    elif l.salary_rule_id.tipo_ingreso == "bonificacion":
                        bonificacion += l.total
                    elif l.salary_rule_id.tipo_ingreso == "incentivos":
                        incentivos += l.total
                    elif l.salary_rule_id.tipo_ingreso == "comisiones":
                        comisiones += l.total
                    elif l.salary_rule_id.tipo_ingreso == "otros_ingresos":
                        otros_ingresos += l.total
                    elif l.salary_rule_id.tipo_ingreso == "bono_horas":
                        bono_horas += l.total
                    elif l.salary_rule_id.tipo_ingreso == "bono_resultados":
                        bono_resultados += l.total
                    elif l.salary_rule_id.tipo_ingreso == "qty_he":
                        qty_he += l.total
                elif l.salary_rule_id.is_descuento == True:
                    if l.salary_rule_id.tipo_descuento == "igss":
                        igss += l.total
                    elif l.salary_rule_id.tipo_descuento == "isr":
                        isr += l.total
                    elif l.salary_rule_id.tipo_descuento == "anticipo1":
                        anticipos1 += l.total
                    elif l.salary_rule_id.tipo_descuento == "anticipo2":
                        anticipos2 += l.total
                    elif l.salary_rule_id.tipo_descuento == "anticipo3":
                        anticipos3 += l.total
                    elif l.salary_rule_id.tipo_descuento == "otros_anticipos":
                        otros_anticipos += l.total
                    elif l.salary_rule_id.tipo_descuento == "prestamo":
                        prestamo += l.total
                    elif l.salary_rule_id.tipo_descuento == "alimentos":
                        alimentos += l.total
                    elif l.salary_rule_id.tipo_descuento == "otros_descuentos":
                        otros_descuentos += l.total
                elif l.salary_rule_id.is_prestacion == True:
                    if l.salary_rule_id.prestaciones == "bono_14":
                        bono14 += l.total
                    elif l.salary_rule_id.prestaciones == "aguinaldo":
                        aguinaldo += l.total
                    elif l.salary_rule_id.prestaciones == "vacaciones":
                        vacaciones += l.total
                    elif l.salary_rule_id.prestaciones == "indemnizacion":
                        indemnizacion += l.total
                    elif l.salary_rule_id.prestaciones == "igss_patronal":
                        igss_patronal += l.total
                    elif l.salary_rule_id.prestaciones == "otra_prestacion":
                        otra_prestacion += l.total
            linea = {
                'item': int(item),
                'periodo': "%s al %s" % (line.date_from, line.date_to),
                'empleado': line.employee_id.name,
                'afiliacion_igss': line.employee_id.igss,
                'dpi': line.employee_id.identification_id,
                'edad': False,
                'sexo': _(line.employee_id.gender),
                'fecha_ingreso': line.contract_id.date_start,
                'nacionalidad': line.employee_id.country_id.name,
                'ocupacion': line.employee_id.job_id.name,
                'fecha_retiro': line.contract_id.date_end,
                'empresa': empresa,
                'salario_base': base or 0.00,
                'dias': dias_trabajados,
                'hr_ordinaria': hr_ordinarias or 0.00,
                'hr_extra': qty_he or 0.00,
                'salario_ordinario': base or 0.00,
                'salario_extra': extras or 0.00,
                'salario_asueto': 0.00,
                'vacaciones': vacaciones or 0.00,
                'salario_total': (base + extras + vacaciones) or 0.00,
                'igss': igss or 0.00,
                'otro_deduccion': (
                                              isr + anticipos1 + anticipos2 + anticipos3 + otros_anticipos + prestamo + alimentos + otros_descuentos) or 0.00,
                'total_deduccion': (
                                               isr + anticipos1 + anticipos2 + anticipos3 + otros_anticipos + prestamo + alimentos + otros_descuentos + igss) or 0.00,
                'otros': (
                                     bono_horas + bono_resultados + bono14 + aguinaldo + indemnizacion + igss_patronal + otra_prestacion) or 0.00,
                'incentivos': (bonificacion + incentivos + comisiones + otros_ingresos) or 0.00,
                'liquido_recibir': ((base + extras + vacaciones) + (
                            bono_horas + bono_resultados + bono14 + aguinaldo + indemnizacion + igss_patronal + otra_prestacion) + (
                                                bonificacion + incentivos + comisiones + otros_ingresos) - (
                                                isr + anticipos1 + anticipos2 + anticipos3 + otros_anticipos + prestamo + alimentos + otros_descuentos + igss)) or 0.00,

            }
            result.append(linea)

        if not result:
            return {}
        else:
            return result

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.payslip.run'].browse(docids)
        recordlines = self._get_report_data(data)
        docargs =  {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'data': data,
            'docs': docs,
            'get_record_lines': recordlines,
        }

        return docargs

