from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class HREmployeeAccountHeads(models.Model):
    _name = 'hr.employee.account.heads'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'HR Employee Account Heads'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    remarks = fields.Text('Remarks')

    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Duplicate Records are not Allowed.')]

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        linked_employee = self.env['hr.employee'].search([('account_head_type', '=', self.id)])
        if linked_employee:
            raise UserError(_('Employee are linked with this Account Head Type, Please First Removed these then Try it.'))
        return super(HREmployeeAccountHeads, self).unlink()


class HRPayScale(models.Model):
    _inherit = 'hr.payscale'

    account_head_id = fields.Many2one('hr.employee.account.heads', 'Account Head Type')


class HRGradeChange(models.Model):
    _inherit = "hr.grade.change"

    def action_approve2(self):
        super().action_approve2()
        for line in self.line_ids:
            if line.employee_id.payscale_id.account_head_id:
                line.employee_id.account_head_type = line.employee_id.payscale_id.account_head_id.id

