import pdb
from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    father_name = fields.Char('Father Name', tracking=True, groups="hr.group_hr_user")
    location_type_id = fields.Many2one('hr.location.type', 'Location Type', groups="hr.group_hr_user")
    location_id = fields.Many2one('hr.location', 'Location', groups="hr.group_hr_user")
    employee_category = fields.Selection([('Head Office', 'Head Office'),
                                          ('Regional Office', 'Regional Office'),
                                          ('Education', 'Educational Institutions'),
                                          ('Other', 'Other')
                                          ], default='Head Office', string='Employee Category', tracking=True, groups="hr.group_hr_user")

    salary_grade = fields.Char('Salary Grade', groups="hr.group_hr_user")
    is_company_vehicle = fields.Boolean('Is Company Vehicle', default=False, groups="hr.group_hr_user")
    to_be = fields.Boolean('To Be', default=False, groups="hr.group_hr_user")

    employee_type = fields.Selection([('executive', 'EXECUTIVE'),
                                      ('non_executive', 'NON EXECUTIVE'),
                                      ('senior_executive', 'SENIOR EXECUTIVE'),
                                      ], string='Employee Type', default='executive', tracking=True, groups="hr.group_hr_user")
    province = fields.Many2one('hr.province', 'Province', tracking=True, groups="hr.group_hr_user")
    # is_airport_duty = fields.Boolean('AirPort Duty?', default=False, tracking=True)
    employee_document_ids = fields.One2many('hr.employee.documents', 'employee_id', 'Employee Documents', groups="hr.group_hr_user")
    is_transport_availed = fields.Boolean('Is Transport Availed', default=False, tracking=True,groups="hr.group_hr_user")
    # transport_area = fields.Selection([('Islamabad', 'Islamabad'),
    #                                    ('Rawalpindi', 'Rawalpindi'),
    #                                    ], string='Transport Area', tracking=True)
    transport_area = fields.Many2one('hr.transport.area', string='Transport Area', tracking=True, groups="hr.group_hr_user")

    is_union_member = fields.Boolean('Is Union Member', default=False, tracking=True, groups="hr.group_hr_user")
    union_id = fields.Many2one('hr.employee.unions', 'Employee Union', tracking=True, groups="hr.group_hr_user")
    # teaching_section = fields.Selection([('Preschool', 'Preschool'),
    #                                      ('Primary', 'Primary'),
    #                                      ('Middle', 'Middle'),
    #                                      ('Secondary', 'Secondary'),
    #                                      ('Higher Secondary', 'Higher Secondary'),
    #                                      ('Graduation', 'Graduation'),
    #                                      ('Masters', 'Masters'),
    #                                      ], string='Teaching Section', tracking=True)
    # branch_id = fields.Many2one('odooschool.campus', 'Campus')
    # dummy_field = fields.Boolean('Dummy', compute='action_update_post_position', store=True)
    admin_teaching_staff = fields.Selection([('Admin', 'Admin'),
                                             ('Teaching', 'Teaching'),
                                             ], string='Admin/Teaching Staff', tracking=True, groups="hr.group_hr_user")

    # @api.depends('branch_id', 'state', 'rebateCateg', 'admin_teaching_staff')
    # def action_update_post_position(self):
    #     for rec in self:
    #         academic_session_id = self.env['odooschool.academic.session'].search([('current', '=', True)], order='id desc', limit=1)
    #         post_recs = self.env['opf.schools.post.position'].search([('branch_id', '=', rec.branch_id.id), ('academic_session_id', '=', academic_session_id.id)])
    #         if post_recs:
    #             for post_rec in post_recs:
    #                 if post_rec.category=='Teaching':
    #                     category = 'Teaching'
    #                 if post_rec.category=='Non Teaching':
    #                     category = 'Admin'
    #                 post_rec.regular = self.env['hr.employee'].search_count([('branch_id', '=', post_rec.branch_id.id),
    #                                                                          ('job_id', '=', post_rec.job_id.id),
    #                                                                          ('employment_nature', '=', 'Permanent'),
    #                                                                          ('admin_teaching_staff', '=', category),
    #                                                                          ('state', '=', 'active')])
    #                 post_rec.temporary = self.env['hr.employee'].search_count([('branch_id', '=', post_rec.branch_id.id),
    #                                                                            ('job_id', '=', post_rec.job_id.id),
    #                                                                            ('employment_nature', '=', 'Contract'),
    #                                                                            ('admin_teaching_staff', '=', category),
    #                                                                            ('state', '=', 'active')])


class HRContract(models.Model):
    _inherit = 'hr.contract'

    adhoc_allowance_2016 = fields.Float('Adhoc Allowance 2016', default=0.00)

    @api.depends('wage', 'allowances_amount', 'personal_pay_amount', 'adhoc_allowance_2016')
    def _compute_gross_salary(self):
        for rec in self:
            rec.gross_salary = rec.wage + rec.allowances_amount + rec.personal_pay_amount + rec.adhoc_allowance_2016
            rec.gross_salary_with_monetization = rec.wage + rec.allowances_amount + rec.monetization_amount + rec.personal_pay_amount + rec.adhoc_allowance_2016

    @api.depends('wage', 'allowances_amount', 'deductions_amount', 'adhoc_allowance_2016', 'personal_pay_amount')
    def _compute_net_salary(self):
        for rec in self:
            rec.net_salary = rec.wage + rec.allowances_amount + rec.adhoc_allowance_2016 + rec.personal_pay_amount + rec.monetization_amount - rec.deductions_amount

    def action_open(self):
        for rec in self:
            rec.state = 'open'

    def action_close(self):
        for rec in self:
            employee_tax_rec = self.env['hr.employee.income.tax'].search([('contract_id', '=', rec.id)])
            if employee_tax_rec:
                tax_adjustment_recs = self.env['hr.employee.income.tax.adjustment'].search([('employee_tax_id', '=', employee_tax_rec.id)])
                contract_payslips = self.env['hr.payslip'].search([('contract_id', '=', rec.id)])
                if (not contract_payslips and not tax_adjustment_recs) or (not contract_payslips and tax_adjustment_recs):
                    if not any([ln.slip_id for ln in employee_tax_rec.employee_tax_lines]):
                        if tax_adjustment_recs:
                            tax_adjustment_recs.write({'state': 'Draft'})
                            tax_adjustment_recs.sudo().unlink()
                        employee_tax_rec.employee_tax_lines.sudo().unlink()
                        employee_tax_rec.state = 'Draft'
                        employee_tax_rec.sudo().unlink()

            # In-Active Allowances
            if rec.allowance_ids:
                for alw_id in rec.allowance_ids:
                    alw_id.write({'expired': True})

            # In-Active Deductions
            if rec.deduction_ids:
                for ded_id in rec.deduction_ids:
                    ded_id.write({'expired': True})

            rec.state = 'close'

    def action_cancel(self):
        for rec in self:
            contract_payslips = self.env['hr.payslip'].search([('contract_id', '=', rec.id)])
            if contract_payslips:
                raise UserError(_('You cannot cancel this contract, Payslips are linked with this Contract. You can Close this Contract.'))

            employee_tax_rec = self.env['hr.employee.income.tax'].search([('contract_id', '=', rec.id)])
            if employee_tax_rec:
                if not any([ln.slip_id for ln in employee_tax_rec.employee_tax_lines]):
                    tax_adjustment_recs = self.env['hr.employee.income.tax.adjustment'].search([('employee_tax_id', '=', employee_tax_rec.id)])
                    if tax_adjustment_recs:
                        tax_adjustment_recs.write({'state': 'Draft'})
                        tax_adjustment_recs.sudo().unlink()
                    employee_tax_rec.employee_tax_lines.sudo().unlink()
                    employee_tax_rec.state = 'Draft'
                    employee_tax_rec.sudo().unlink()

            # In-Active Allowances
            if rec.allowance_ids:
                for alw_id in rec.allowance_ids:
                    alw_id.write({'expired': True})

            # In-Active Deductions
            if rec.deduction_ids:
                for ded_id in rec.deduction_ids:
                    ded_id.write({'expired': True})

            # Cancel Employee Salary Inputs created from computer arrears button
            emp_salary_inputs = self.env['hr.emp.salary.inputs'].search([('description', '=', str(rec.id))])
            if emp_salary_inputs:
                if not any([emp_input_id.slip_id for emp_input_id in emp_salary_inputs]):
                    emp_salary_inputs.write({'state': 'cancel'})
                else:
                    raise ValidationError(_('Arrears and Prev. Deduction Inputs are linked with Payslips.'))
            rec.state = 'cancel'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError('You can not delete Record that are not in Draft or Cancel.')
        return super(HRContract, self).unlink()

    # this is used in the Cron job for deletion of Zero Allowance and Deductions
    @api.model
    def extra_alw_unlink(self):
        contracts = self.env['hr.contract'].search([('notes', '!=', 'OPF')], limit=50)
        for contract in contracts:
            for alw in contract.deduction_ids:
                flag = False
                for line in alw.deduction_id.percentage_ids:
                    if line.domain:
                        if self.env['hr.employee'].search(safe_eval(line.domain) + [('id', '=', contract.employee_id.id)]):
                            flag = True
                if not flag:
                    alw.sudo().unlink()
            contract['notes'] = 'OPF'


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    province_id = fields.Many2one('hr.province', 'Province', compute="_compute_slip_employee_data", store=True)
    employee_type = fields.Selection([('executive', 'EXECUTIVE'),
                                      ('non_executive', 'NON EXECUTIVE'),
                                      ('senior_executive', 'SENIOR EXECUTIVE'),
                                      ], string='Employee Type', tracking=True, compute="_compute_slip_employee_data", store=True)

    location_type_id = fields.Many2one('hr.location.type', 'Location Type', compute="_compute_slip_employee_data", store=True)
    location_id = fields.Many2one('hr.location', 'Location')
    employee_category = fields.Selection([('Head Office', 'Head Office'),
                                          ('Regional Office', 'Regional Office'),
                                          ('Education', 'Educational Institutions'),
                                          ('Other', 'Other')
                                          ], string='Employee Category', tracking=True, compute="_compute_slip_employee_data", store=True)

    payscale_category = fields.Many2one('hr.payscale.category', 'Payscale Category', compute="_compute_slip_employee_data", store=True)
    employee_code = fields.Char('Employee Code', compute="_compute_slip_employee_data", store=True)

    @api.depends('employee_id')
    def _compute_slip_employee_data(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
                rec.province_id = rec.employee_id.province and rec.employee_id.province.id or False
                rec.employee_type = rec.employee_id.employee_type and rec.employee_id.employee_type or ''
                rec.location_type_id = rec.employee_id.location_type_id and rec.employee_id.location_type_id.id or False
                rec.location_id = rec.employee_id.location_id and rec.employee_id.location_id.id or False
                rec.employee_category = rec.employee_id.employee_category and rec.employee_id.employee_category or ''
                rec.payscale_category = rec.employee_id.payscale_category and rec.employee_id.payscale_category.id or False
                if not rec.payscale_id:
                    rec.payscale_id = rec.employee_id.payscale_id and rec.employee_id.payscale_id.id or False


class HREmployeeDocuments(models.Model):
    _name = 'hr.employee.documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Documents"

    name = fields.Char("Document Name")
    sequence = fields.Integer('Sequence')
    serial_no = fields.Integer('Serial No', default=1)
    date = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    file_attachment = fields.Binary(string='Attachment', help='Upload the file')

    @api.model
    def create(self, values):
        serial_no = 1
        if values.get('employee_id', False):
            prev_rec = self.env['hr.employee.documents'].search([('employee_id', '=', values['employee_id'])], order='serial_no')
            if prev_rec:
                serial_no = prev_rec.serial_no + 1
        result = super(HREmployeeDocuments, self).create(values)
        result.serial_no = serial_no
        return result


class HREmployeeUnions(models.Model):
    _name = 'hr.employee.unions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Unions"

    name = fields.Char("Union Name")
    sequence = fields.Integer('Sequence')
    code = fields.Char('Code')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(HREmployeeUnions, self).unlink()


class HRGradeChangeLine(models.Model):
    _inherit = "hr.grade.change.line"

    location_type_id = fields.Many2one('hr.location.type', 'Location Type')
    location_id = fields.Many2one('hr.location', 'Location')

    def action_approve2(self):
        for line in self.line_ids:
            if not line.no_action:
                if line.new_grade.id==line.grade.id and line.new_stage==line.stage and line.personal_pay_count==line.employee_id.personal_pay_count:
                    raise UserError(_('Employee %s have same new payscale %s as its previous %s') % (line.employee_id.name, line.new_grade.name, line.grade.name))

                # Close Previous Contract
                old_contract = self.close_contract(line.employee_id)
                line.employee_id.write({'payscale_id': line.new_grade.id,
                                        'stage': line.new_stage,
                                        'personal_pay_count': line.personal_pay_count,
                                        'department_id': line.department_id and line.department_id.id or False,
                                        'job_id': line.job_id and line.job_id.id or False,
                                        'location_type_id': line.location_type_id and line.location_type_id.id or False,
                                        'location_id': line.location_id and line.location_id.id or False})
                # Create New Contract
                self.create_contract(line.employee_id, line, old_contract)
            else:
                line.remarks = 'Penalty Issue'
        self.state = 'approve'
