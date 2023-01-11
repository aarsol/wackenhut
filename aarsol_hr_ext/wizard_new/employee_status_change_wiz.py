from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
import pdb


class EmployeeStatusChangeWiz(models.TransientModel):
    _name = 'employee.status.change.wiz'
    _description = 'Employee State Change Wizard'

    def _get_employee_ids(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    employee_ids = fields.Many2many('hr.employee', 'employee_status_change_wiz_rel', 'wiz_id', 'employee_id', 'Employee(s)', default=_get_employee_ids)
    date = fields.Date('Date', default=fields.Date.today(), required=True)
    office_order_file = fields.Image(string='Office Order', attachment=True, help='Upload the file')

    state = fields.Selection([('active', 'Active'),
                              ('terminated', 'Terminated'),
                              ('resigned', 'Resigned'),
                              ('retired', 'Retired'),
                              ('com_retired', 'Compulsory Retired'),
                              ('removal', 'Removal From Service'),
                              ('dismissal', 'Dismissal From Service'),
                              ('deceased', 'Deceased'),
                              ('archive', 'Archived')
                              ], string='Status')

    termination_option = fields.Selection([('notice_period', 'Notice Period'),
                                           ('immediate', 'Immediate')
                                           ], string='Resignation Option')
    notice_period_start_date = fields.Date('Notice Period Start Date')
    notice_period_end_date = fields.Date('Notice Period End Date')
    termination_date = fields.Date('Resignation Date')

    payroll_status = fields.Selection([('start', 'Start'),
                                       ('stop', 'Stop'),
                                       ], string='Payroll Status')

    def action_status_change(self):
        for rec in self:
            if rec.employee_ids:
                for employee_id in rec.employee_ids:
                    if employee_id.state in ('terminated',
                                             'resigned',
                                             'retired',
                                             'com_retired',
                                             'removal',
                                             'dismissal',
                                             'deceased',
                                             'archive'):
                        raise UserError(_("You cannot Change the State."))

                    # Close Employee Contracts
                    contracts = self.env['hr.contract'].search([('employee_id', '=', employee_id.id), ('state', 'not in', ('close', 'cancel'))])
                    if contracts:
                        for contract in contracts:
                            if not rec.state=='resigned':
                                if rec.notice_period_end_date:
                                    contract.date_end = rec.notice_period_end_date
                                else:
                                    contract.date_end = rec.date
                                contract.action_close()

                            if rec.state=='resigned':
                                if rec.termination_option and rec.termination_option=='notice_period':
                                    if rec.notice_period_end_date:
                                        contract.date_end = rec.notice_period_end_date
                                        today = fields.Date.today()
                                        if rec.notice_period_end_date <= today:
                                            contract.action_close()
                                else:
                                    contract.action_close()

                    # Create Record in the Employee Status History
                    history_data_values = {
                        'employee_id': employee_id.id,
                        'department_id': employee_id.department_id and employee_id.department_id.id or False,
                        'designation_id': employee_id.job_id and employee_id.job_id.id or False,
                        'date': rec.date,
                        'old_status': employee_id.state,
                        'new_status': rec.state,
                        'state': 'lock',
                        'office_order_file': rec.office_order_file,
                    }
                    new_history_rec = self.env['hr.employee.status.history'].create(history_data_values)

                    # Change Employee Status
                    employee_id.write({'state': rec.state})

                    if rec.state=='resigned':
                        employee_id.write({'termination_option': rec.termination_option,
                                           'notice_period_start_date': rec.notice_period_start_date,
                                           'notice_period_end_date': rec.notice_period_end_date,
                                           'termination_date': rec.termination_date})
                        if rec.payroll_status:
                            employee_id.payroll_status = rec.payroll_status
