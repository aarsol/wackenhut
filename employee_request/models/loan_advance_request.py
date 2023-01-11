import pdb
from odoo import models, fields, api
from odoo.exceptions import UserError


class LoanAdvanceRequest(models.Model):
    _name = 'loan.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Loan Advance Request'
    _rec_name = 'employee_id'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', tracking=True)
    department_id = fields.Many2one(
        'hr.department', related='employee_id.department_id', store=True)
    amount = fields.Integer("Amount", tracking=True)
    apply_date = fields.Date('Request Date', tracking=True, index=True)
    purpose = fields.Text('Purpose', tracking=True)

    forward_to_ho = fields.Boolean('Forward to Head Office')
    head_office_approval = fields.Boolean('Head Office Approval')
    forward = fields.Boolean('forward')

    hod_app = fields.Boolean('HOD App')
    hr_app = fields.Boolean('HR App')
    pro_app = fields.Boolean('PRO App')
    fin_app = fields.Boolean('FIN App')

    parent_dept_hod = fields.Boolean('Parent Dept HOD')
    sub_parent_dept_hod = fields.Boolean('Sub Parent Dept HOD')
    loan_advance = fields.Selection(selection=[('loan', 'Loan'),
                                               ('advance', 'Salary Advance'),
                                               ('permanent_withdraw',
                                                'Permanent Withdraw'),
                                               ], string='Type', default='loan', index=True, tracking=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ('reject', 'Reject'),
                              ], string='Status', default='draft', tracking=True, index=True)
    emp_approved = fields.Many2many('hr.employee')
    emp_approval = fields.Many2one('hr.employee', )
    emp_approval_department = fields.Many2one('hr.department')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    def create_activity(self):
        self.activity_schedule(
            'employee_request.mail_act_loan_request', user_id=self.emp_approval.user_id.id)

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
            result.write({'emp_approved': [(4, result.emp_approval.id)]})
            result.emp_approval_department = result.employee_id.department_id

        if report_to!=hod:
            result.emp_approval = result.employee_id.parent_id
            if not result.emp_approval.user_id:
                result.unlink()
                raise UserError('User Not Assigned To Manager')
            result.write({'emp_approved': [(4, result.emp_approval.id)]})

        result.create_activity()
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('loan.request')
        return result

    def approve_request(self):
        if self.state=='approved':
            raise UserError('Request Already Approved')

        hr = self.env['hr.employee'].sudo().search(
            ['&', ('department_id', '=', 'Human Resource Department'), ('job_id', '=', 'Head of HR')])
        prorector = self.env['hr.employee'].sudo().search(
            [('job_id', '=', 'Prorector')], order='id', limit=1)
        finance = self.env['hr.employee'].sudo().search(
            [('department_id', '=', 'Accounts office'), ('job_id', '=', 'Treasurer')])

        if self.emp_approval==hr:
            if not finance.user_id:
                raise UserError('User Not Assigned To Finance')
            self.emp_approval = finance
            self.create_activity()
            return True

        if self.emp_approval==finance and self.fin_app is False:
            if not prorector.user_id:
                raise UserError('User Not Assigned To Prorector')
            self.emp_approval = prorector
            self.fin_app = True
            self.create_activity()
            return True

        if self.emp_approval==finance and self.fin_app is True:
            if self.forward_to_ho==True and self.head_office_approval==True:
                self.state = 'approved'
                if self.loan_advance=="advance":
                    self.action_create_employee_loan()
                if self.loan_advance=="loan":
                    self.action_create_employee_pf_loan()
                if self.loan_advance=="permanent_withdraw":
                    self.action_create_employee_pf_permanent_withdraw()
            else:
                raise UserError('Need Head Office Approval')
            return True

        if self.emp_approval==prorector:
            if not finance.user_id:
                raise UserError('User Not Assigned To Finance')
            self.emp_approval = finance
            self.create_activity()
            return True

        # this for when hod and report to is not same and request assign to report to
        if not self.emp_approval_department and self.emp_approval==self.employee_id.parent_id:
            department_manager = self.employee_id.department_id.manager_id
            department = self.employee_id.department_id

            # if report_to is not equal to hod then assign activity to hod
            if self.employee_id!=department_manager:
                if not department_manager.user_id:
                    raise UserError('User Not Assigned To Manager')
                self.emp_approval = department_manager
                self.emp_approval_department = department
                self.write({'emp_approved': [(4, self.emp_approval.id)]})
                self.create_activity()
                return True
            else:
                if self.employee_id.department_id:
                    parent_department_check = self.employee_id.department_id
                else:
                    if not hr.user_id:
                        raise UserError('User Not Assigned To Hr')
                    self.emp_approval = hr
                    self.write({'emp_approved': [(4, self.emp_approval.id)]})
                    self.create_activity()
                    parent_department_check = False
                    return True

                # this loop checking recursively for parent department
                while (len(parent_department_check) > 0):
                    if not self.emp_approval_department:
                        self.emp_approval_department = self.employee_id.department_id
                        self.emp_approval = self.emp_approval_department.manager_id
                    else:
                        self.emp_approval_department = self.emp_approval_department.parent_id
                        self.emp_approval = self.emp_approval_department.manager_id

                    if self.emp_approval:
                        if self.emp_approval not in self.emp_approved:
                            if not self.emp_approval.user_id:
                                raise UserError('User Not Assigned To Manager')
                            self.write(
                                {'emp_approved': [(4, self.emp_approval.id)]})
                            self.create_activity()
                            parent_department_check = False
                            return True
                    parent_department_check = self.emp_approval_department.parent_id

                if not self.emp_approval_department.parent_id:
                    if not hr.user_id:
                        raise UserError('User Not Assigned To Hr')
                    self.emp_approval = hr
                    self.create_activity()
                    return True
                return True

        # this for checking parent department if yes then assign activity to parent else it assign to hr
        if self.emp_approval_department:
            if self.emp_approval_department.parent_id and self.emp_approval_department.parent_id.manager_id not in self.emp_approved:
                self.emp_approval_department = self.emp_approval_department.parent_id
                self.emp_approval = self.emp_approval_department.manager_id
                if not self.emp_approval.user_id:
                    raise UserError('User Not Assigned to Manager')
                self.write({'emp_approved': [(4, self.emp_approval.id)]})
                self.create_activity()
                return True

            if self.emp_approval_department.parent_id:
                parent_department_check = self.emp_approval_department.parent_id
            else:
                if not hr.user_id:
                    raise UserError('User Not Assigned To Hr')
                self.emp_approval = hr
                self.write({'emp_approved': [(4, self.emp_approval.id)]})
                self.create_activity()
                parent_department_check = False
                return True

            while len(parent_department_check) > 0:
                if self.emp_approval_department.parent_id:
                    self.emp_approval_department = self.emp_approval_department.parent_id
                    self.emp_approval = self.emp_approval_department.manager_id

                if self.emp_approval:
                    if self.emp_approval not in self.emp_approved:
                        if not self.emp_approval:
                            raise UserError('User Not Assigned To Manager')
                        self.write(
                            {'emp_approved': [(4, self.emp_approval.id)]})
                        self.create_activity()
                        parent_department_check = False
                        return True
                parent_department_check = self.emp_approval_department.parent_id

            if not self.emp_approval_department.parent_id:
                if not hr.user_id:
                    raise UserError('User Not Assigned To HR')
                self.emp_approval = hr
                self.write({'emp_approved': [(4, self.emp_approval.id)]})
                self.create_activity()
            return True

    def reject_request(self):
        self.hod_app = True
        for rec in self:
            rec.state = 'reject'

    def action_create_employee_loan(self):
        loan_rule_id = self.env['hr.loans'].search([('code', '=', 'SAD')])
        if not loan_rule_id:
            loan_rule_id = self.env['hr.loans'].search(
                [], order='id asc', limit=1)
        loan_dict_values = {
            'employee_id': self.employee_id.id,
            'employee_code': self.employee_id.code,
            'loan_id': loan_rule_id and loan_rule_id.id or False,
            'retirement_date': self.employee_id.retirement_date,
            'amount': self.amount,
            'num_quotas': loan_rule_id and loan_rule_id.shares_max or 0,
            'date_start': self.apply_date,
            'date_payment': self.apply_date,
            'payment_channel': 'bank',
            'is_eligible': True,
            'accounts_required': False,
            'old_data': False,
        }
        loan_rec = self.env['hr.loan'].create(loan_dict_values)
        loan_rec.loan_confirm()
        loan_rec.loan_pay()

    def action_create_employee_pf_loan(self):
        pf_profile_id = self.env['hr.employee.cp.fund.profile'].search(
            [('employee_id', '=', self.employee_id.id), ('state', 'in', ('Draft', 'Done'))], order='id desc', limit=1)
        loan_dict_values = {
            'employee_id': self.employee_id.id,
            'amount': self.amount,
            'recommended_amount': self.amount,
            'installments': 12,
            'date': self.apply_date,
            'pf_profile_id': pf_profile_id and pf_profile_id.id,
        }
        new_loan_rec = self.env['hr.cp.fund.loan'].create(loan_dict_values)
        new_loan_rec.action_done()

    def action_create_employee_pf_permanent_withdraw(self):
        pf_profile_id = self.env['hr.employee.cp.fund.profile'].search(
            [('employee_id', '=', self.employee_id.id), ('state', 'in', ('Draft', 'Done'))], order='id desc', limit=1)
        loan_dict_values = {
            'employee_id': self.employee_id.id,
            'amount': self.amount,
            'recommended_amount': self.amount,
            'pf_profile_id': pf_profile_id and pf_profile_id.id,
        }
        new_loan_rec = self.env['hr.cp.fund.permanent.withdrawal'].create(
            loan_dict_values)
        new_loan_rec.action_done()
