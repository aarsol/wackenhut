from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class HRPayrollRuleHeads(models.Model):
    _name = 'hr.payroll.rule.heads'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'HR Payroll Rule Heads'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule', tracking=True)
    account_head_type = fields.Many2one('hr.employee.account.heads', 'Account Head Type', tracking=True)
    account_id = fields.Many2one('account.account', 'GL Account', tracking=True)
    date = fields.Date('Date', default=fields.Date.today())
    debit_credit_type = fields.Selection([('debit', 'Debit'),
                                          ('credit', 'Credit')
                                          ], string='Type', default='debit', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    remarks = fields.Text('Remarks')

    _sql_constraints = [('name_unique', 'UNIQUE(salary_rule_id,account_head_type,account_id)', 'Duplicate Records are not Allowed.')]

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(HRPayrollRuleHeads, self).unlink()

    def action_read_hr_payroll_rule_heads(self):
        self.ensure_one()
        return {
            'name': "HR Payroll Rule Heads Form",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.rule.heads',
            'res_id': self.id,
        }
