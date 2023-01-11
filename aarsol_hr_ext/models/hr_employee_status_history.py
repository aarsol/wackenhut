from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
import logging

_logger = logging.getLogger(__name__)


class HREmployeeStatusHistory(models.Model):
    _name = 'hr.employee.status.history'
    _description = 'Employee Status History'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', string='Employee Name')
    designation_id = fields.Many2one('hr.job', string='Designation', compute='_compute_employee_info', store=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_employee_info', store=True)
    old_status = fields.Selection([('active', 'Active'),
                                   ('terminated', 'Terminated'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('com_retired', 'Compulsory Retired'),
                                   ('removal', 'Removal From Service'),
                                   ('dismissal', 'Dismissal From Service'),
                                   ('deceased', 'Deceased'),
                                   ('archive', 'Archived')
                                   ], string='Old Status', index=True, tracking=True)
    new_status = fields.Selection([('active', 'Active'),
                                   ('terminated', 'Terminated'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('com_retired', 'Compulsory Retired'),
                                   ('removal', 'Removal From Service'),
                                   ('dismissal', 'Dismissal From Service'),
                                   ('deceased', 'Deceased'),
                                   ('archive', 'Archived')
                                   ], string='New Status', index=True, tracking=True)
    date = fields.Date('Date', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked'),
                              ], default='draft', string='Status', tracking=True)
    office_order_file = fields.Image(string='Office Order', attachment=True)

    @api.depends('employee_id')
    def _compute_employee_info(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.designation_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    @api.model
    def create(self, values):
        result = super(HREmployeeStatusHistory, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.status.history')
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise ValidationError(_("You can delete the Records that are in the Draft State!"))
        super(HREmployeeStatusHistory, self).unlink()
