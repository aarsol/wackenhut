from odoo import models, fields, api, _
import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from odoo.tools import date_utils
from odoo.tools.safe_eval import safe_eval
import re
import pdb
from odoo.http import content_disposition, Controller, request, route
from odoo.exceptions import ValidationError, UserError
import json


class TimeOffRequest(models.Model):
    _name = 'special.hr.leave'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'UCP Time Off'
    _rec_name = 'employee_id'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    department_id = fields.Many2one('hr.department', string="Department")
    next_on_duty = fields.Many2one('hr.employee', string="Next On Duty Name")
    date_from = fields.Date(string='Date From', default=fields.Date.today())
    date_to = fields.Date(string='Date To', default=fields.Date.today())
    compensatory_date_from = fields.Date("Compensatory Date From")
    compensatory_date_to = fields.Date("Compensatory Date To")
    leave_ids = fields.One2many('hr.leave', 'leave_id')
    hod_app = fields.Boolean(default=False)
    hr_app = fields.Boolean(default=False)
    pro_app = fields.Boolean(default=False)
    parent_dept_hod = fields.Boolean(default=False)
    sub_parent_dept_hod = fields.Boolean(default=False)
    other = fields.Boolean(string="Other", default=False)
    sub_type_id = fields.Many2one('hr.leave.type', string="Sub Leave Type")
    leave_purpose = fields.Char("Purpose of Leave")
    number_of_days = fields.Float(
        'Duration (Days)', compute='_compute_number_of_days')
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('confirm', 'To Approved'),
                   ('approve', 'Approved'), ('reject', 'Reject'), ],
        string='State', default='draft', tracking=True, index=True)
    emp_approved = fields.Many2many('hr.employee')
    emp_approval = fields.Many2one('hr.employee', )
    emp_approval_department = fields.Many2one('hr.department')
    upload_documents = fields.Binary('Attachment')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    """
    This compute method calculate number of days.....
    """

    @api.depends('date_from', 'date_to')
    def _compute_number_of_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                rec.number_of_days = (rec.date_to - rec.date_from).days + 1

    def create_activity(self):
        self.activity_schedule(
            'employee_request.mail_act_special_leave_request', user_id=self.emp_approval.user_id.id)

    """
    This method is create to check the eligibility criteria of employee leave request
    """

    @api.model
    def create(self, values):

        result = super().create(values)

        report_to = result.employee_id.parent_id.id
        hod = result.employee_id.department_id.manager_id.id

        # if result.employee_id.probation==True and result.leave_type_id.annual_leave==False:
        #     result.sudo().unlink()
        #     raise UserError(
        #         "Annual leave not allowed during probation period..")

        if result.employee_id.employment_nature=='visiting' and result.leave_type_id.visiting_leave==False:
            result.sudo().unlink()
            raise UserError(
                "Visiting Employee are not allowed for any kind of leave..")

        if report_to==hod:
            if not result.employee_id.department_id.manager_id.user_id:
                result.sudo().unlink()
                raise UserError('User Not Assigned To Manager')
            result.write({
                'emp_approved': [(4, result.employee_id.department_id.manager_id.id)],
            })
            result.emp_approval = result.employee_id.department_id.manager_id
            result.emp_approval_department = result.employee_id.department_id

        if report_to!=hod:
            if not result.employee_id.parent_id.user_id:
                result.sudo().unlink()
                raise UserError('User Not Assigned To Manager')
            result.write({
                'emp_approved': [(4, result.employee_id.parent_id.id)],
            })
            result.emp_approval = result.employee_id.parent_id

        result.create_activity()
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code(
                'special.hr.leave')

        return result

    """
    This method is create for when hod approved the request its state change to to approved state and create activity for HR
    """

    def approve_request(self):

        if self.state=='approved':
            raise UserError('Request Already Approved')

        hr = self.env['hr.employee'].sudo().search(
            ['&', ('department_id', '=', 'Human Resource Department'), ('job_id', '=', 'Head of HR')])
        prorector = self.env['hr.employee'].sudo().search(
            [('job_id', '=', 'Prorector')], limit=1, order='id')

        if self.emp_approval==hr:
            if not prorector.user_id:
                raise UserError('User Not Assigned TO Prorector')
            self.emp_approval = prorector
            self.create_activity()
            return True
        if self.emp_approval==prorector:
            self.state = 'approve'
            return True

        # this for when hod and report to is not same and request assign to report to
        if not self.emp_approval_department and self.emp_approval==self.employee_id.parent_id:
            department_manager = self.employee_id.department_id.manager_id
            department = self.employee_id.department_id

            # if report_to is not equal to hod then assign activity to hod
            if self.employee_id!=department_manager:
                # if not department_manager.user_id:
                #     raise UserError('User Not Assigned To Manager')
                self.emp_approval = department_manager
                self.emp_approval_department = department
                self.write({
                    'emp_approved': [(4, self.emp_approval.id)],
                })
                self.create_activity()
                return True
            else:
                if self.employee_id.department_id:
                    parent_department_check = self.employee_id.department_id
                else:
                    # if not hr.user_id:
                    #     raise UserError('User Not Assigned To HR')
                    self.emp_approval = hr
                    self.write({
                        'emp_approved': [(4, self.emp_approval.id)],
                    })
                    self.create_activity()
                    parent_department_check = False
                    return True

                # this loop checking recursively for parent department
                while (len(parent_department_check) > 0):
                    if not self.emp_approval_department:
                        # if not self.employee_id.department_id.manager_id.user_id:
                        #     raise UserError('User Not Assigned To Manager')
                        self.emp_approval_department = self.employee_id.department_id
                        self.emp_approval = self.emp_approval_department.manager_id

                    else:
                        # if not self.emp_approval_department.parent_id.manager_iduser_id:
                        #     raise UserError('User Not Assigned to Manager')

                        self.emp_approval_department = self.emp_approval_department.parent_id
                        self.emp_approval = self.emp_approval_department.manager_id

                    if self.emp_approval:
                        if self.emp_approval not in self.emp_approved:
                            # if not self.emp_approval.user_id:
                            #     raise UserError('User Not Assigned To User')
                            self.write({
                                'emp_approved': [(4, self.emp_approval.id)],
                            })
                            self.create_activity()
                            parent_department_check = False
                            return True
                    parent_department_check = self.emp_approval_department.parent_id

                if not self.emp_approval_department.parent_id:
                    # if not hr.user_id:
                    #     raise UserError('User Not Assigned To HR')
                    self.emp_approval = hr
                    self.create_activity()
                    return True
                return True
        # this for checking parent department if yes then assign activity to parent else it assign to hr
        if self.emp_approval_department:
            if self.emp_approval_department.parent_id and self.emp_approval_department.parent_id.manager_id not in self.emp_approved:
                self.emp_approval_department = self.emp_approval_department.parent_id
                # if self.emp_approval_department.manager_id.user_id:
                #     raise UserError('User Not Assigned to Manager')
                self.emp_approval = self.emp_approval_department.manager_id
                self.write({
                    'emp_approved': [(4, self.emp_approval.id)],
                })
                self.create_activity()
                return True

            if self.emp_approval_department.parent_id:
                parent_department_check = self.emp_approval_department.parent_id
            else:
                # if not hr.user_id:
                #     raise UserError('User Not Assigned to Hr')
                self.emp_approval = hr
                self.write({
                    'emp_approved': [(4, self.emp_approval.id)],
                })
                self.create_activity()
                parent_department_check = False
                return True

            while (len(parent_department_check) > 0):
                if self.emp_approval_department.parent_id:
                    # if not self.emp_approval_department.parent_id.manager_id.user_id:
                    #     raise UserError('User Not Assigned to Manager')
                    self.emp_approval_department = self.emp_approval_department.parent_id
                    self.emp_approval = self.emp_approval_department.manager_id

                if self.emp_approval:
                    if self.emp_approval not in self.emp_approved:
                        # if not self.emp_approval.user_id:
                        #     raise UserError('User Not Assigned to Manager')
                        self.write({
                            'emp_approved': [(4, self.emp_approval.id)],
                        })
                        self.create_activity()
                        parent_department_check = False
                        return True
                parent_department_check = self.emp_approval_department.parent_id

            if not self.emp_approval_department.parent_id:
                # if not hr.user_id:
                #     raise UserError('User Not Assigned To HR')
                self.emp_approval = hr
                self.write({
                    'emp_approved': [(4, self.emp_approval.id)],
                })
                self.create_activity()

            return True

    def reject_request(self):
        self.pro_app = True
        for rec in self:
            rec.state = 'reject'

            notification_ids = []
            if rec.employee_id:
                hr_employee = self.env['hr.employee'].search(
                    [('department_id.name', '=', 'Human Resource Department'), ('job_id.name', '=', 'Head of HR')])
                partner_id = [
                    rec.user_id.partner_id.id for rec in hr_employee if rec.user_id.partner_id.id]
                if not self.employee_id.user_id:
                    raise UserError("Currently no User Assign to employee..")
                partner_id.append(self.employee_id.user_id.partner_id.id)
                for rec in partner_id:
                    if rec:
                        notification_ids.append((0, 0, {
                            'res_partner_id': rec,
                            'notification_type': 'inbox'
                        }))
                self.env['mail.message'].create(
                    {
                        'message_type': 'notification',
                        'model': self._name,
                        'res_id': self.id,
                        'partner_ids': partner_id,
                        'body': 'Employee leave request not approved by Prorector....',
                        'notification_ids': notification_ids,
                    })

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_id = rec.employee_id and rec.employee_id or ''
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False

    @api.model
    def write(self, values):
        if values.get('emp_approval') is not None:
            reporting_employee = self.env['hr.employee'].sudo().search(
                [('id', '=', int(values['emp_approval']))])
            if not reporting_employee.user_id:
                raise UserError('User Not Assigned To Reporting Employee')

        return super().write(values)
