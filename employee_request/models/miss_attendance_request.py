from odoo import models, fields, api
from datetime import datetime, time
from dateutil import relativedelta
from odoo.exceptions import UserError


class MissedAttendance(models.Model):
    _name = 'missed.attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Missed Attendance Request'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', tracking=True, index=True)
    checkin = fields.Boolean('Check In', tracking=True)
    checkout = fields.Boolean('Check Out', tracking=True)
    checkin_date = fields.Datetime('Check In Date', tracking=True)
    checkout_date = fields.Datetime('Check Out Date', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Approved'),
                              ('reject', 'reject'),
                              ], string='Status', default='draft', tracking=True, index=True)
    reason = fields.Text(string='Reason')
    application_date = fields.Datetime(
        string='Application Date', default=fields.Datetime.now(), readonly=True)
    attendance_id = fields.Many2one('hr.attendance', 'Attendance')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    def create_activity(self):
        self.activity_schedule('employee_request.mail_act_resign_request',
                               user_id=self.employee_id.parent_id.user_id.id)

    @api.model
    def create(self, values):
        result = super().create(values)
        for rec in result:
            if not rec.employee_id.parent_id:
                result.unlink()
                raise UserError(
                    'This employee has not any Reporting Officer.')
            elif not rec.employee_id.parent_id.user_id:
                result.unlink()
                raise UserError(
                    'No User assigned To Manager.')

        result.create_activity()

        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code(
                'missed.attendance')
        return result

    def action_approved(self):
        for rec in self:
            data = {'employee_id': rec.employee_id.id}
            if rec.checkin and rec.checkout:
                data.update({'check_in': rec.checkin_date,
                             'check_out': rec.checkout_date,
                             })
                self.env['hr.attendance'].create(data)

            if rec.checkin:
                checkin_day = self.env['hr.attendance'].search([('employee_id', '=', rec.employee_id.id),
                                                                ('check_in', '>=', datetime.combine(rec.checkin_date,
                                                                                                    time.min) + relativedelta.relativedelta(
                                                                    hours=-5)),
                                                                ('check_in', '<=', datetime.combine(rec.checkin_date,
                                                                                                    time.max) + relativedelta.relativedelta(
                                                                    hours=-5))
                                                                ], order='id asc', limit=1)
                if checkin_day:
                    checkin_day.check_in = rec.checkin_date
                    rec.attendance_id = checkin_day.id

                if not checkin_day:
                    checkin_day = self.env['hr.attendance'].search([('employee_id', '=', rec.employee_id.id),
                                                                    ('check_out', '>=',
                                                                     datetime.combine(rec.checkin_date,
                                                                                      time.min) + relativedelta.relativedelta(
                                                                         hours=-5)),
                                                                    ('check_out', '<=',
                                                                     datetime.combine(rec.checkin_date,
                                                                                      time.max) + relativedelta.relativedelta(
                                                                         hours=-5))
                                                                    ], order='id asc', limit=1)
                    if checkin_day:
                        checkin_day.check_in = rec.checkin_date
                        rec.attendance_id = checkin_day.id

                if not checkin_day:
                    checkin_data_values = {
                        'employee_id': rec.employee_id.id,
                        'check_in': rec.checkin_date,
                        'type': 'regular',
                    }
                    checkin_day = self.env['hr.attendance'].create(
                        checkin_data_values)
                    rec.attendance_id = checkin_day.id

            if rec.checkout:
                checkout_day = self.env['hr.attendance'].search([('employee_id', '=', rec.employee_id.id),
                                                                 ('check_in', '>=', datetime.combine(rec.checkout_date,
                                                                                                     time.min) + relativedelta.relativedelta(
                                                                     hours=-5)),
                                                                 ('check_in', '<=', datetime.combine(rec.checkout_date,
                                                                                                     time.max) + relativedelta.relativedelta(
                                                                     hours=-5))
                                                                 ], order='id asc', limit=1)
                if checkout_day:
                    checkout_day.check_out = rec.checkout_date
                    rec.attendance_id = checkout_day.id
            rec.state = 'approve'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'
