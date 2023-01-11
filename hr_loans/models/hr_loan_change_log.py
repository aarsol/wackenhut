import time
from datetime import datetime

import numpy_financial as npf
from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HRLoanChangeLog(models.Model):
    _name = "hr.loan.change.log"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Loan Change Log"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    date = fields.Date('Date', tracking=True)
    notes = fields.Text(string="Description", tracking=True)
    loan_id = fields.Many2one('hr.loan', 'Loan Ref.')

    @api.model
    def create(self, values):
        res = super(HRLoanChangeLog, self).create(values)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('hr.loan.change.log')
        return res
