from odoo import models, fields, api, _
import pdb


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    loan_ids = fields.One2many('hr.loan', 'employee_id', 'Employee Loans', groups="hr.group_hr_user")
