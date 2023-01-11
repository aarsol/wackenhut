import time
from datetime import datetime

import numpy_financial as npf
from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HRSupplementaryLoan(models.Model):
    _name = "hr.supplementary.loan"
    _description = "HR Supplementary Loans"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", ondelete='cascade')
    move_id = fields.Many2one('account.move', 'Move Ref')
    date = fields.Date('Date')
    notes = fields.Text(string="Notes")
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel'),
                              ], default='draft', string='Status')
    to_be = fields.Boolean(string='To Be', default=False)

    @api.model
    def create(self, values):
        res = super(HRSupplementaryLoan, self).create(values)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('hr.supplementary.loan')
        return res
