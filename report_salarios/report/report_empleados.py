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

from odoo import api, models
import time
import datetime


class LiquidoReport(models.AbstractModel):
    _name = 'report.report_salarios.template_reporte_liquido'

    def _get_report_data(self,record_ids):
        # pool = pooler.get_pool(cr.dbname)
        hr_rule = self.env['hr.salary.rule']
        # hr_payslip = self.env['hr.payslip.run'].browse(record_ids)
        # Nomina consolidada de un numero de emplados
        # hr_payslip_line = self.pool.get('hr.payslip') #Nomina por Empleado
        result = []
        empleado = ""
        cui = ""
        nit = ""
        cuenta = ""
        # departamento = ""
        # area = ""
        # estatus = "Activo"
        empresa = ""
        nomina = ""
        periodo = ""
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
        # bono14 = 0.00
        # aguinaldo = 0.00
        # vacaciones = 0.00
        # indemnizacion = 0.00
        # igss_patronal = 0.00
        # otra_prestacion = 0.00
        no = 0
        user = self.env['res.users'].browse(self._uid)
        for line in record_ids:
            # empresa = user.company_id.name
            nomina = line.name
            periodo = "Del %s al %s" % (line.date_start, line.date_end)
            for hr in line.slip_ids:
                no += 1
                empleado = hr.employee_id.name
                # area = hr.employee_id.department_id.parent_id.name
                cui = hr.employee_id.identification_id
                nit = ""
                cuenta = hr.employee_id.bank_account_id.acc_number
                # departamento = hr.contract_id.job_id.department_id.name
                # if hr.employee_id.active == False:
                #	estatus = "Inactivo"
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
                # bono14 = 0.00
                # aguinaldo = 0.00
                # vacaciones = 0.00
                # indemnizacion = 0.00
                # igss_patronal = 0.00
                # otra_prestacion = 0.00
                for l in hr.line_ids:
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
                # elif l.salary_rule_id.is_prestacion == True:
                #	if l.salary_rule_id.prestaciones == "bono_14":
                #		bono14 += l.total
                #	elif l.salary_rule_id.prestaciones == "aguinaldo":
                #		aguinaldo += l.total
                #	elif l.salary_rule_id.prestaciones == "vacaciones":
                #		vacaciones += l.total
                #	elif l.salary_rule_id.prestaciones == "indemnizacion":
                #		indemnizacion += l.total
                #	elif l.salary_rule_id.prestaciones == "igss_patronal":
                #		igss_patronal += l.total
                #	elif l.salary_rule_id.prestaciones == "otra_prestacion":
                #		otra_prestacion += l.total
                linea = {
                    'no': int(no),
                    'empresa': user.company_id.name,
                    'nomina': nomina,
                    'empleado': empleado,
                    'cui': cui,
                    'nit': nit,
                    'cuenta': cuenta,
                    # 'depto': departamento,
                    # 'estatus': estatus,
                    # 'area': area,
                    'salario': base,
                    'boni_decreto': (bonificacion + incentivos) or '0.00',
                    'qty_he': qty_he or '0.00',
                    'hr_extra': ((((base*4) + (bonificacion*4) + incentivos)/30)/8) or '0.00',
                    'total_he': extras or '0.00',
                    'bono_hrs': bono_horas or '0.00',
                    'bono_resultados': bono_resultados or '0.00',
                    'total_ingresos': (
                                              base + bonificacion + incentivos + extras + bono_horas + bono_resultados + comisiones + otros_ingresos) or '0.00',
                    'igss': igss or '0.00',
                    'isr': isr or '0.00',
                    'anticipo_1': anticipos1 or '0.00',
                    'anticipo_2': anticipos2 or '0.00',
                    'anticipo_3': anticipos3 or '0.00',
                    'total_descuentos': (
                                                igss + isr + anticipos1 + anticipos2 + anticipos3 + otros_anticipos + prestamo + alimentos + otros_descuentos) or '0.00',
                    'total_liquido': ((
                                              base + bonificacion + incentivos + extras + bono_horas + bono_resultados + comisiones + otros_ingresos) - (
                                              igss + isr + anticipos1 + anticipos2 + anticipos3 + otros_anticipos + prestamo + alimentos + otros_descuentos)) or '0.00',
                    # 'igss_patronal': igss_patronal or '0.00',
                    # 'bono_anual': bono14 or '0.00',
                    # 'aguinaldo': aguinaldo or '0.00',
                    # 'indemnizacion':indemnizacion or '0.00',
                    # 'vacaciones': vacaciones or '0.00',
                    # 'total_acumulado':(igss_patronal + bono14 + aguinaldo + indemnizacion + vacaciones + otra_prestacion) or '0.00',
                }
                result.append(linea)

        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.payslip.run'].browse(docids)
        recordlines = self._get_report_data(docs)
        docargs =  {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip.run',
            'data': data,
            'docs': docs,
            'get_record_lines': recordlines,
        }
        return docargs
