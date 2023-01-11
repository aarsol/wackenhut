import time
from datetime import datetime

import numpy_financial as npf
from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HRLoanGuarantor(models.Model):
    _name = "hr.loan.guarantor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Loan Guarantors"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Guarantor')
    department_id = fields.Many2one('hr.department', 'Department', compute='_compute_employee_info', store=True)
    job_id = fields.Many2one('hr.job', 'Designation', compute='_compute_employee_info', store=True)
    amount = fields.Float('Amount')
    date = fields.Date('Date', tracking=True, default=fields.Date.today())
    loan_id = fields.Many2one('hr.loan', 'Loan Ref.')
    notes = fields.Text(string="Description", tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Lock'),
                              ], string='Status', default='draft')
    gratuity_amount = fields.Float('Gratuity Amount')

    @api.model
    def create(self, values):
        res = super(HRLoanGuarantor, self).create(values)
        return res

    @api.depends('employee_id')
    def _compute_employee_info(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.job_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False
