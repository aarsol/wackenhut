import pdb
import time
import json
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
import logging

_logger = logging.getLogger(__name__)


def parse_date(td):
    resYear = float(td.days) / 365.0
    resMonth = (resYear - int(resYear)) * 365.0 / 30.0
    resDays = int((resMonth - int(resMonth)) * 30)
    resYear = int(resYear)
    resMonth = int(resMonth)
    return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (resMonth and (str(resDays) + "D") or "")


class HREmployeeHalfPayLeaveRequest(models.Model):
    _name = 'hr.employee.half.pay.leave.request'
    _description = 'Employee Half Pay Leave Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete="restrict")
    employee_code = fields.Char(string='Employee Code', compute='_compute_employee_info', store=True)
    job_id = fields.Many2one('hr.job', string='Designation', compute='_compute_employee_info', store=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_employee_info', store=True)
    date = fields.Date('Request Date', tracking=True, default=fields.Date.today())
    date_from = fields.Date('Date From', tracking=True, default=fields.Date.today())
    date_to = fields.Date('Date To', tracking=True)
    leave_period = fields.Char('Leave Period', compute='_compute_leave_period', store=True)
    duty_resume_request = fields.Many2one('hr.employee.duty.resume.request', 'Resume Request', tracking=True, index=True)
    show_turn_to_draft = fields.Boolean('Show Turn to Draft', compute='_compute_show_turn_to_draft', store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Approved'),
                              ('reject', 'Reject')
                              ], default='draft', string='Status', tracking=True)
    remarks = fields.Text('Remarks')

    @api.depends('employee_id')
    def _compute_employee_info(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.job_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'
            rec.employee_id.write({'half_pay_leave': True,
                                   'half_pay_leave_start_date': rec.date_from,
                                   'half_pay_leave_end_date': rec.date_to})

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    def action_turn_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def create(self, values):
        result = super(HREmployeeHalfPayLeaveRequest, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.half.pay.leave.request')
        body = "Half Pay Leave Request From " + result.date_from.strftime('%d-%m-%Y') + " To " + result.date_to.strftime("%d-%m-%Y") + " Generated."
        result.employee_id.message_post(body=body)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise ValidationError(_("You can delete the Records that are in the Draft State!"))
        super(HREmployeeHalfPayLeaveRequest, self).unlink()

    @api.constrains('date_from', 'date_to')
    def date_period_constrains(self):
        for rec in self:
            if rec.date_to and rec.date_from and rec.date_from > rec.date_to:
                raise ValidationError(_('Date From should be Before Date End'))
            if rec.date and rec.date_from and rec.date_from < rec.date:
                raise ValidationError(_('Date From Should be Greater then Request Date.'))

    @api.depends('date_from', 'date_to')
    def _compute_leave_period(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                start = datetime.strptime(str(rec.date_from), OE_DFORMAT)
                end = datetime.strptime(str(rec.date_to), OE_DFORMAT)
                delta = end - start
                rec.leave_period = parse_date(delta)
            else:
                rec.leave_period = ''

    @api.depends('state', 'duty_resume_request')
    def _compute_show_turn_to_draft(self):
        for rec in self:
            flag = False
            if rec.state=='approve' and rec.duty_resume_request:
                flag = True
            rec.show_turn_to_draft = flag

    @api.constrains('employee_id', 'date_from', 'date_to')
    def request_duplicate_constrains(self):
        for rec in self:
            if rec.employee_id and rec.date_from and rec.date_to:
                duplicate_request = self.env['hr.employee.half.pay.leave.request'].search([('employee_id', '=', rec.employee_id.id),
                                                                                           ('date_from', '>=', rec.date_from),
                                                                                           ('date_to', '<=', rec.date_to),
                                                                                           ('state', '!=', 'reject'),
                                                                                           ('id', '!=', rec.id)])
                if duplicate_request:
                    raise ValidationError(_('Half Pay Leave Request for this Employee already Exist For specified Period'))


class HREmployeeDutyResumeRequest(models.Model):
    _name = 'hr.employee.duty.resume.request'
    _description = 'Employee Duty Resume  Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True, ondelete="restrict")
    employee_code = fields.Char(string='Employee Code', compute='_compute_employee_info', store=True)
    job_id = fields.Many2one('hr.job', string='Designation', compute='_compute_employee_info', store=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_employee_info', store=True)
    date = fields.Date('Request Date', tracking=True, default=fields.Date.today())
    duty_resume_date = fields.Date('Duty Resume Date', default=fields.Date.today())
    half_pay_request = fields.Many2one('hr.employee.half.pay.leave.request', 'Half Pay Request', tracking=True, index=True, auto_join=True, ondelete='cascade')
    request_type = fields.Selection([('half_leave', 'Return From Half Pay Leave'),
                                     ], string='Request Type', tracking=True, index=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Approved'),
                              ('reject', 'Reject')
                              ], default='draft', string='Status', tracking=True)
    remarks = fields.Text('Remarks')

    @api.depends('employee_id')
    def _compute_employee_info(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.job_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'
            rec.employee_id.write({'half_pay_leave': False,
                                   'half_pay_leave_end_date': rec.duty_resume_date})
            if rec.duty_resume_date < rec.half_pay_request.date_to:
                rec.half_pay_request.remarks = 'Employee Request to Resume Duty Before Approved Period'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    def action_turn_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def create(self, values):
        half_pay_request = False
        if values.get('employee_id', False):
            # check whether record for this employee exists or not
            half_pay_request = self.env['hr.employee.half.pay.leave.request'].search([('employee_id', '=', values['employee_id']), ('state', '!=', 'reject')])
            if not half_pay_request:
                raise ValidationError(_('Half Pay Leave Request for this Employee does not Exist.'))

            # Check Existing Record if it already have duty resume request
            if half_pay_request and half_pay_request.duty_resume_request:
                raise ValidationError(_('Half Pay Leave Request Already have Duty Resume Request.'))

        result = super(HREmployeeDutyResumeRequest, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.duty.resume.request')

        if half_pay_request:
            half_pay_request.duty_resume_request = result.id
            result.half_pay_request = half_pay_request.id

        body = "Duty Resume Request has been Generated."
        result.employee_id.message_post(body=body)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise ValidationError(_("You can delete the Records that are in the Draft State!"))
        super(HREmployeeDutyResumeRequest, self).unlink()
