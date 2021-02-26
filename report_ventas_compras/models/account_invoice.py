# -*- encoding: UTF-8 -*-
##############################################################################

from odoo import fields, models, api, _

class AccountInvoice(models.Model):
	_inherit = "account.move"
	
	serie_factura = fields.Char(string="Serie Factura", required=False, help="Serie de la factura de proveedor")
	num_factura = fields.Char(string="Numero Factura", required=False, help="Numero de la factura de proveedor")
	tipo_documento = fields.Selection([
		('FC', 'Factura Cambiaria'),
		('FE', 'Factura Especial'),
		('FCE', 'Factura Electronica'),
                ('FAC', 'Factura'),
                ('FEL', 'FEL'),
		('NC', 'Nota de Credito'),
		('ND', 'Nota de Debito'),
		('FPC', 'Factura Peq. Contribuyente'),
		('DA', 'Declaracion Unica Aduanera'),
		('FA', 'FAUCA'),
		('FO', 'Formulario SAT'),
		('ONAF', 'Otros No Afectos'),
		('EP', 'Escritura Publica')],'Tipo Documento', default='FC', required=True, help="Tipo de documento de gasto que se reflejara en el libro de Ventas/Compras del IVA")
AccountInvoice()
