from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class HREmployeePayrollStatus(models.Model):
    _name = "hr.employee.payroll.status"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Employee Payroll Status"

    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Employee', tracking=True)
    date = fields.Date('Date', tracking=True)
    payroll_status = fields.Selection([('start', 'Start'),
                                       ('stop', 'Stop')
                                       ], string='Payroll Status', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    remarks = fields.Text('Remarks')

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def name_get(self):
        res = []
        for record in self:
            name = (record.employee_id.name or '') + ' - ' + record.payroll_status
            res.append((record.id, name))
        return res


class EmployeePayrollStatusUpdateWiz(models.TransientModel):
    _name = 'employee.payroll.status.update.wiz'
    _description = 'Employee Payroll Status Update Wizard'

    @api.model
    def _get_employee(self):
        if self.env.context.get('active_model', False)=='hr.employee' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    @api.model
    def _get_old_payroll_status(self):
        payroll_status = ''
        if self.env.context.get('active_model', False)=='hr.employee' and self.env.context.get('active_id', False):
            payroll_status = self.env['hr.employee'].search([('id', '=', self.env.context.get('active_id', False))]).payroll_status
        return payroll_status

    employee_id = fields.Many2one('hr.employee', string='Employee', default=_get_employee, required=True)
    date = fields.Date('Date', default=fields.Date.today(), required=True)
    payroll_status = fields.Selection([('start', 'Start'),
                                       ('stop', 'Stop')
                                       ], string='Payroll Status', required=True)
    old_payroll_status = fields.Selection([('start', 'Start'),
                                           ('stop', 'Stop')
                                           ], string='Old Payroll Status', default=_get_old_payroll_status)

    def action_update_payroll_status(self):
        for rec in self:
            status_values = {
                'employee_id': rec.employee_id and rec.employee_id.id or False,
                'date': rec.date,
                'payroll_status': rec.payroll_status,
                'state': 'lock'
            }
            rec.employee_id.payroll_status = rec.payroll_status
            new_rec = self.env['hr.employee.payroll.status'].create(status_values)
