from odoo import models, fields, api, _
import pdb


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    account_head_type = fields.Many2one('hr.employee.account.heads', 'Account Head Type', tracking=True, groups="hr.group_hr_user")


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)
