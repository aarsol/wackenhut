from odoo import models, fields, api
from odoo.exceptions import UserError


class LeaveRequestInherit(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def create(self, values):
        emp = self.env['hr.employee'].sudo().search([('id', '=', int(values['employee_id']))])
        if not emp.parent_id:
            raise UserError('This employee has not any Reporting Officer.')

        # Remarked By Sarfraz @ 14-07-2022
        # if not emp.parent_id.user_id:
        #     raise UserError('No User Assigned To Manager.')
        result = super().create(values)
        return result
