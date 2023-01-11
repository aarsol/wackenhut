from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    promotion_ids = fields.One2many('hr.employee.promotion', 'employee_id', 'Promotions')
    demotion_ids = fields.One2many('hr.employee.demotion', 'employee_id', 'Demotions')
    transfer_ids = fields.One2many('hr.employee.transfer', 'employee_id', 'Transfers')
