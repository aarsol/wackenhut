import pdb

from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import UserError


class ResignRequest(models.Model):
    _name = 'resign.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Resign Request'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', tracking=True)
    resign_from = fields.Date(string='Notice Period Date', tracking=True)
    current_date = fields.Date(
        "Current Date", default=lambda self: str(datetime.now()))
    apply_date = fields.Date('Resign Date', tracking=True)
    resign_reason = fields.Text('Reason', tracking=True)
    hod_app = fields.Boolean(default=False)
    pro_app = fields.Boolean(default=False)
    hr_app = fields.Boolean(default=False)
    parent_dept_hod = fields.Boolean(default=False)
    sub_parent_dept_hod = fields.Boolean(default=False)
    write_state = fields.Char()
    state = fields.Selection([('notice period', 'Notice Period'),
                              ('approved', 'Approved'),
                              ('withdraw', 'Withdraw'),
                              ('reject', 'Reject'),
                              ], string='Status', default='notice period', tracking=True, index=True)
    emp_approved = fields.Many2many('hr.employee')
    emp_approval = fields.Many2one('hr.employee', )
    emp_approval_department = fields.Many2one('hr.department')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    """
    This method is called when current date and Notice period are equal its call automatically..
    """

    @api.model
    def resign_request_method(self):
        for rec in self:
            if rec.resign_from==rec.current_date and rec.state=='approved':
                rec.employee_id.state = 'resigned'

    @api.onchange('state')
    def state_change(self):
        for rec in self:
            if rec.state=='notice period':
                payroll_status = self.env['hr.employee.payroll.status'].search(
                    [('employee_id', '=', rec.employee_id.id)])
                if payroll_status:
                    payroll_status.payroll_status = 'stop'
                else:
                    self.env['hr.employee.payroll.status'].create({
                        'employee_id': rec.employee_id.id,
                        'payroll_status': 'stop',
                        'company_id': rec.employee_id.company_id and rec.employee_id.company_id.id or False,
                    })
            if rec.state=='reject' or rec.state=='withdraw':
                payroll_status = self.env['hr.employee.payroll.status'].search(
                    [('employee_id', '=', rec.employee_id.id)])
                if payroll_status:
                    payroll_status.payroll_status = 'start'
                else:
                    self.env['hr.employee.payroll.status'].create({
                        'employee_id': rec.employee_id.id,
                        'payroll_status': 'start',
                        'company_id': rec.employee_id.company_id and rec.employee_id.company_id.id or False,
                    })

    def notice_period_request(self):
        for rec in self:
            rec.state = 'notice period'

    def approve_request(self):
        self.pro_app = True
        for rec in self:
            rec.state = 'approved'

    def withdraw_request(self):
        for rec in self:
            rec.state = 'withdraw'

    def create_activity(self):

        self.activity_schedule(
            'employee_request.mail_act_resign_request', user_id=self.emp_approval.user_id.id)

    @api.model
    def create(self, values):
        result = super().create(values)
        report_to = result.employee_id.parent_id.id
        hod = result.employee_id.department_id.manager_id.id

        # if report_to and hod is same then request approval send to hod
        if report_to==hod:
            result.emp_approval = result.employee_id.department_id.manager_id
            if not result.emp_approval.user_id:
                result.unlink()
                raise UserError('User Not Assigned To Manager')
            result.write({
                'emp_approved': [(4, result.emp_approval.id)],
            })
            result.write({
                'emp_approved': [(4, result.employee_id.id)],
            })
            result.emp_approval_department = result.employee_id.department_id

        if report_to!=hod:
            result.emp_approval = result.employee_id.parent_id
            if not result.emp_approval.user_id:
                result.unlink()

                raise UserError('User Not Assigned To Manager')
            result.write({
                'emp_approved': [(4, result.emp_approval.id)],
            })
            result.write({
                'emp_approved': [(4, result.employee_id.id)],
            })

        result.create_activity()
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code(
                'resign.request')
        return result

    def approve_request(self):

        if self.state=='approved':
            raise UserError('Request Already Approved')

        hr = self.env['hr.employee'].sudo().search(
            ['&', ('department_id', '=', 'Human Resource Department'), ('job_id', '=', 'Head of HR')])
        prorector = self.env['hr.employee'].sudo().search(
            [('job_id', '=', 'Prorector')], limit=1, order='id')

        if self.emp_approval==hr:
            if not prorector.user_id:
                raise UserError('User Not Assigned To Prorector')
            self.emp_approval = prorector
            self.create_activity()
            return True
        if self.emp_approval==prorector:
            self.state = 'approved'
            return True

        # this for when hod and report to is not same and request assign to report to
        if not self.emp_approval_department and self.emp_approval==self.employee_id.parent_id:
            department_manager = self.employee_id.department_id.manager_id
            department = self.employee_id.department_id

            # if report_to is not equal to hod then assign activity to hod
            if self.employee_id!=department_manager:
                if not department_manager.user_id:
                    raise UserError('No User Assigned To Manager')
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
                    if not hr.user_id:
                        raise UserError('No User Assigned To Hr')
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
                        self.emp_approval_department = self.employee_id.department_id
                        if not self.emp_approval_department.manager_id.user_id:
                            raise UserError('User Not Assigned To Manager')
                        self.emp_approval = self.emp_approval_department.manager_id

                    else:
                        self.emp_approval_department = self.emp_approval_department.parent_id
                        if not self.emp_approval_department.manager_id.user_id:
                            raise UserError('User Not Assigned To Manager')
                        self.emp_approval = self.emp_approval_department.manager_id

                    if self.emp_approval:
                        if self.emp_approval not in self.emp_approved:
                            if not self.emp_approval.user_id:
                                raise UserError('User Not Assigned To Manager')

                            self.write({
                                'emp_approved': [(4, self.emp_approval.id)],
                            })
                            self.create_activity()
                            parent_department_check = False
                            return True
                    parent_department_check = self.emp_approval_department.parent_id

                if not self.emp_approval_department.parent_id:
                    if hr.user_id is not False:
                        raise UserError('User Not Assigned To HR')
                    self.emp_approval = hr
                    self.create_activity()
                    return True
                return True
        # this for checking parent department if yes then assign activity to parent else it assign to hr
        if self.emp_approval_department:
            if self.emp_approval_department.parent_id and self.emp_approval_department.parent_id.manager_id not in self.emp_approved:
                self.emp_approval_department = self.emp_approval_department.parent_id
                if not self.emp_approval_department.manager_id.user_id:
                    raise UserError('User Not Assigned To Manager')
                self.emp_approval = self.emp_approval_department.manager_id
                self.write({
                    'emp_approved': [(4, self.emp_approval.id)],
                })
                self.create_activity()
                return True

            if self.emp_approval_department.parent_id:
                parent_department_check = self.emp_approval_department.parent_id
            else:
                if not hr.user_id:
                    raise UserError('User Not Assigned To Hr')
                self.emp_approval = hr
                self.write({
                    'emp_approved': [(4, self.emp_approval.id)],
                })
                self.create_activity()
                parent_department_check = False
                return True

            while (len(parent_department_check) > 0):
                if self.emp_approval_department.parent_id:
                    self.emp_approval_department = self.emp_approval_department.parent_id
                    if not self.emp_approval_department.manager_id:
                        raise UserError('User Not Assigned To Manager')
                    self.emp_approval = self.emp_approval_department.manager_id

                if self.emp_approval:
                    if self.emp_approval not in self.emp_approved:
                        if not self.emp_approval.user_id:
                            raise UserError('User Not Assigned To Manager')
                        self.write({
                            'emp_approved': [(4, self.emp_approval.id)],
                        })
                        self.create_activity()
                        parent_department_check = False
                        return True
                parent_department_check = self.emp_approval_department.parent_id

            if not self.emp_approval_department.parent_id:
                if not hr.user_id:
                    raise UserError('User Not Assigned to Hr')
                self.emp_approval = hr
                self.write({
                    'emp_approved': [(4, self.emp_approval.id)],
                })
                self.create_activity()

            return True

    def reject_request(self):
        for rec in self:
            self.env['hr.employee'].search(
                [('id', '=', rec.employee_id.id)]).write({'state': 'active', 'payroll_status': 'start'})

            employee_contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
            employee_contract.date_end = None

            payroll_status = self.env['hr.employee.payroll.status'].search(
                [('employee_id', '=', rec.employee_id.id)])
            if payroll_status:
                payroll_status.payroll_status = 'start'
            else:
                self.env['hr.employee.payroll.status'].create({
                    'employee_id': rec.employee_id.id,
                    'payroll_status': 'start',
                    'company_id': rec.employee_id.company_id and rec.employee_id.company_id.id or False,
                })
            rec.state = 'reject'

    @api.onchange('resign_from')
    def contract_date(self):
        employee_contract = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
        employee_contract.date_end = self.resign_from
