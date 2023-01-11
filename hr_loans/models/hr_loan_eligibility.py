from odoo import models, fields, api, _
import pdb


class HRLoansEligibility(models.Model):
    _name = 'hr.loan.eligibility'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Eligibility Criteria'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code', tracking=True)
    sequence = fields.Integer('Sequence')
    domain = fields.Char('Domain Rule')
    period = fields.Char('Months', tracking=True)
    loan_rule_id = fields.Many2one('hr.loans', 'Loan Rule', tracking=True)
