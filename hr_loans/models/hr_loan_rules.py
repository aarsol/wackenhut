from odoo import models, fields, api, _
import pdb


class HRLoans(models.Model):
    _name = 'hr.loans'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Rules'

    name = fields.Char('Name', size=128, required=True)
    sequence = fields.Integer('Sequence', default=10)
    code = fields.Char('Code', size=64, required=True, )
    active = fields.Boolean('Active', help="If the active field is set to false, it will allow you to hide the Loan Rule without removing it.", default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    amount_max = fields.Float('Loan Amount', required=True, )
    shares_max = fields.Float('No. of Installments', required=True, )
    amount_percentage = fields.Float('(%) of Basic', required=True, help='Share amount of Loan per Payslip should be in the threshold value', default=30.0)
    note = fields.Text('Description')
    journal_id = fields.Many2one('account.journal', 'Loan Journal', required=True)
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule', tracking=True)
    interest_salary_rule_id = fields.Many2one('hr.salary.rule', 'Interest Salary Rule', tracking=True)

    interest_rate = fields.Float('Interest Rate (%)', tracking=True)
    apply_on_remaining_service = fields.Boolean('Apply On Remaining Service', default=False, tracking=True)
    eligibility_ids = fields.One2many('hr.loan.eligibility', 'loan_rule_id', 'Eligibility Criteria')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
