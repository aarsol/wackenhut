from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class EmployeeMedicalAdvance(models.Model):
    _name = "medical.advance"
    _description = "Employee Medical Advance Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    request_date = fields.Date("Request Date", default=fields.Datetime.now, tracking=True)
    reason = fields.Text("Reason")
    amount = fields.Char("Amount", tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ], default='draft', string='Status', tracking=True, index=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    def action_draft(self):
        self.state = 'approved'

    def action_approved(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(EmployeeMedicalAdvance, self).unlink()

    @api.model
    def create(self, values):
        record = super(EmployeeMedicalAdvance, self).create(values)
        if not record.name:
            record.name = self.env['ir.sequence'].next_by_code('medical.advance')
        return record
