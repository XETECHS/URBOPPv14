from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mobile = fields.Char(required=True)


#class AccountMove(models.Model):
#    _inherit = 'account.move'

#    fel_serie = fields.Integer(string='Serie FEL')
#    fel_no = fields.Integer(string='No. FEL')


   # @api.one
   # @api.constrains('mobile', 'email')
   # def _check_mobile_email(self):
   #     if self.search(['|', ('mobile', '=', self.mobile), ('email', '=', self.email)]).filtered(lambda r: self.customer and not r.parent_id and r.id != self.id):
   #         raise ValidationError("%s or %s already exixts"%(self.mobile or '.', self.email or '.'))
