# -*- encoding: UTF-8 -*-
##############################################################################
from odoo import fields, models, api, _

class ProductTemplate(models.Model):
	_inherit = "product.template"
	
	tipo_gasto = fields.Selection([
		('compra', 'Compra/Venta'),
		('servicio', 'Servicios/Honorarios'),
		('combustibles', 'Combustibles/Lubricantes'),
		('importacion', 'Importaciones'),
		('exportacion', 'Exportaciones'), 
		('n/a', 'N/A')],'Tipo Gasto', required=False, default='compra', help="Tipo de gasto que se reflejara en el libro de Ventas/Compras del IVA")

ProductTemplate()
