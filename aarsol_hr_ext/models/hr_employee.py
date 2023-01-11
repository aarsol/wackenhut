from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from odoo.tools import date_utils
from odoo.tools.safe_eval import safe_eval
import re
import pdb

import logging

_logger = logging.getLogger(__name__)


def parse_date(td):
    resYear = float(td.days) / 365.0
    resMonth = (resYear - int(resYear)) * 365.0 / 30.0
    resDays = int((resMonth - int(resMonth)) * 30)
    resYear = int(resYear)
    resMonth = int(resMonth)
    return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (
            resMonth and (str(resDays) + "D") or "")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    code = fields.Char('Code', groups="hr.group_hr_user")
    cnic = fields.Char('CNIC', size=15, tracking=True, groups="hr.group_hr_user")

    street = fields.Char('Street', groups="hr.group_hr_user")
    street2 = fields.Char('Street2', groups="hr.group_hr_user")
    city = fields.Char('City', groups="hr.group_hr_user")
    zip = fields.Char('Zip', change_default=True, groups="hr.group_hr_user")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]", groups="hr.group_hr_user")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', groups="hr.group_hr_user")
    age = fields.Char("Age", compute='_compute_age', groups="hr.group_hr_user")
    age2 = fields.Char("Age (Yearly)", help="This field is used in the Age calculation for yearly, used in EOBI", groups="hr.group_hr_user")
    charge_eobi = fields.Boolean('Charge EOBI', compute='_calc_charge_eobi', store=True, default=False, groups="hr.group_hr_user")

    joining_date = fields.Date('Joining Date', groups="hr.group_hr_user")
    payment_mode = fields.Selection([('bank', 'Bank'),
                                     ('cash', 'Cash'),
                                     ('cheque', 'Cheque'),
                                     ('demand_draft', 'Demand Draft'),
                                     ], default='bank', string='Payment Mode', tracking=True, groups="hr.group_hr_user")
    bank_account_title = fields.Char('Account Title', groups="hr.group_hr_user")
    bank_account_no = fields.Char('Account No', groups="hr.group_hr_user")
    bank_id = fields.Many2one('res.bank', 'Old Bank', groups="hr.group_hr_user")
    hr_bank_id = fields.Many2one('hr.bank', 'Bank', groups="hr.group_hr_user")
    bank_location = fields.Char('Bank Location', tracking=True, groups="hr.group_hr_user")
    bank_branch = fields.Char('Bank Branch', tracking=True, groups="hr.group_hr_user")

    section_id = fields.Many2one('hr.section', 'Section', groups="hr.group_hr_user")
    category_id = fields.Many2one('hr.category', 'Category', groups="hr.group_hr_user")

    publications = fields.Integer('No of Publication', tracking=True, groups="hr.group_hr_user")
    rate_per_publication = fields.Float('Rate Per Publication', tracking=True, groups="hr.group_hr_user")
    increment_date = fields.Date('Increment Date', tracking=True, groups="hr.group_hr_user")

    leaving_date = fields.Date('Date Of Leaving', groups="hr.group_hr_user")
    retirement_date = fields.Date('Retirement Date', compute='_compute_retirement_date', store=True, groups="hr.group_hr_user")
    retired = fields.Boolean('Retired', default=False, groups="hr.group_hr_user")

    # rebateCateg = fields.Boolean('Rebate Categ')
    rebateCateg = fields.Selection([('teaching', 'Teaching'),
                                    ('non_teaching', 'Non Teaching'),
                                    ('other', 'Other')
                                    ], string='Rebate Category', tracking=True, groups="hr.group_hr_user")

    appointment_mode_id = fields.Char('Appointment Mode', groups="hr.group_hr_user")
    pension_bit = fields.Char('Pension Bit', groups="hr.group_hr_user")
    to_be = fields.Boolean('To Be', default=False, groups="hr.group_hr_user")

    medical_ids = fields.One2many('hr.employee.medical', 'employee_id', 'Medical History', groups="hr.group_hr_user")
    operation_area_id = fields.Many2one('hr.employee.operation.area', string='Operation Area', groups="hr.group_hr_user")
    family_ids = fields.One2many('hr.employee.family', 'employee_id', 'Family', groups="hr.group_hr_user")
    academic_ids = fields.One2many('hr.employee.academic', 'employee_id', 'Academics', groups="hr.group_hr_user")
    experience_ids = fields.One2many('hr.experience', 'employee_id', 'Experience information', groups="hr.group_hr_user")

    manual_slips = fields.Integer(string='Manual Slips', tracking=True, groups="hr.group_hr_user")
    manual_gross = fields.Float(string='Manual Gross', tracking=True, groups="hr.group_hr_user")
    manual_tax = fields.Float(string='Manual Tax', tracking=True, groups="hr.group_hr_user")
    rem_slips = fields.Integer(string='Remaining Slips', tracking=True, groups="hr.group_hr_user")

    gross_salary = fields.Float(compute='get_salary_comp', store=True, groups="hr.group_hr_user")
    tax_deducted = fields.Float(compute='get_salary_comp', store=True, groups="hr.group_hr_user")
    future_salary = fields.Float(compute='get_salary_comp', store=True, groups="hr.group_hr_user")

    basic_pay_type = fields.Selection([('fixed', 'Fixed'),
                                       ('scale_base', 'Scale Base'),
                                       ], default='fixed', string='Basic Pay Type', tracking=True, groups="hr.group_hr_user")
    payscale_category = fields.Many2one('hr.payscale.category', 'Payscale Category', tracking=True, groups="hr.group_hr_user")
    payscale_id = fields.Many2one('hr.payscale', 'Payscale', tracking=True, groups="hr.group_hr_user")
    stage = fields.Integer('Stage', groups="hr.group_hr_user")
    total_service = fields.Char("Total Service", compute='_compute_total_service',groups="hr.group_hr_user")
    employment_nature = fields.Selection([('Permanent', 'PERMANENT'),
                                          ('Contract', 'CONTRACT'),
                                          ('Deputation', 'DEPUTATION'),
                                          ('Fixed', 'FIXED'),
                                          ('internee', 'INTERNEE'),
                                          ('contingency', 'CONTINGENCY'),
                                          ], default='Permanent', string='Employment Nature', index=True, tracking=True,groups="hr.group_hr_user")

    allowance_template_id = fields.Many2one('hr.salary.allowances.template', 'Allowance Template', tracking=True,groups="hr.group_hr_user")
    deduction_template_id = fields.Many2one('hr.salary.deductions.template', 'Deduction Template', tracking=True, groups="hr.group_hr_user")
    personal_pay_count = fields.Integer('Personal Pays', default=0, groups="hr.group_hr_user")
    profile_state = fields.Selection([('draft', 'Draft'),
                                      ('lock', 'Lock'),
                                      ], default='draft', string='Profile State', tracking=True, groups="hr.group_hr_user")
    payroll_status = fields.Selection([('start', 'Start'),
                                       ('stop', 'Stop'),
                                       ], string='Payroll Status', default='start', tracking=True, groups="hr.group_hr_user")
    state = fields.Selection([('active', 'Active'),
                              ('terminated', 'Terminated'),
                              ('resigned', 'Resigned'),
                              ('retired', 'Retired'),
                              ('com_retired', 'Compulsory Retired'),
                              ('removal', 'Removal From Service'),
                              ('dismissal', 'Dismissal From Service'),
                              ('deceased', 'Deceased'),
                              ('archive', 'Archived'),
                              ], string='Status', default='active', index=True, tracking=True, groups="hr.group_hr_user")
    confirmation_date = fields.Date('Confirmation Date', groups="hr.group_hr_user")
    regularization_date = fields.Date('Regularization Date', groups="hr.group_hr_user")
    termination_option = fields.Selection([('notice_period', 'Notice Period'),
                                           ('immediate', 'Immediate')
                                           ], string='Termination Option', groups="hr.group_hr_user")
    notice_period_start_date = fields.Date('Notice Period Start Date', tracking=True, groups="hr.group_hr_user")
    notice_period_end_date = fields.Date('Notice Period End Date', tracking=True, groups="hr.group_hr_user")
    termination_date = fields.Date('Termination Date', tracking=True, groups="hr.group_hr_user")
    status_history_ids = fields.One2many('hr.employee.status.history', 'employee_id', 'Status History', groups="hr.group_hr_user")
    re_appointed = fields.Boolean('Re-Appointed', default=False, tracking=True, groups="hr.group_hr_user")

    half_pay_leave = fields.Boolean('Half Pay Leave', tracking=True, groups="hr.group_hr_user")
    half_pay_leave_start_date = fields.Date('Half Pay Leave Start Date', tracking=True, groups="hr.group_hr_user")
    half_pay_leave_end_date = fields.Date('Half Pay Leave End Date', tracking=True, groups="hr.group_hr_user")
    emp_promotion_ids = fields.One2many('hr.grade.change.line', 'employee_id', 'Promotion History', groups="hr.group_hr_user")

    # Employee Disability
    any_disability = fields.Boolean('Any Disability?', default=False, tracking=True, groups="hr.group_hr_user")
    disability_nature_id = fields.Many2one('hr.employee.disability.nature', 'Disability Nature', tracking=True, groups="hr.group_hr_user")
    disability_detail = fields.Char('Disability Detail', groups="hr.group_hr_user")
    religion = fields.Many2one('hr.religion', 'Religion', groups="hr.group_hr_user")

    blood_group = fields.Selection([('A+', 'A+ve'),
                                    ('B+', 'B+ve'),
                                    ('O+', 'O+ve'),
                                    ('AB+', 'AB+ve'),
                                    ('A-', 'A-ve'),
                                    ('B-', 'B-ve'),
                                    ('O-', 'O-ve'),
                                    ('AB-', 'AB-ve')],
                                   'Blood Group', default='A+', tracking=True, groups="hr.group_hr_user")

    # contract_type = fields.Selection([('full_time', 'Full Time'),
    #                                   ('part_time', 'Part Time'),
    #                                   ('visiting', 'Visiting'),
    #                                   ], string='Contract Type', groups="hr.group_hr_user")
    
    probation = fields.Boolean('Probation')
    dual_nationality = fields.Boolean(string="Dual Nationality", default=False, groups="hr.group_hr_user")
    
    def name_get(self):
        res = []
        for record in self:
            name = (record.code or '') + ' - ' + record.name
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)

    def _compute_age(self):
        for rec in self:
            if rec.birthday:
                start = datetime.strptime(str(rec.birthday), OE_DFORMAT)
                end = datetime.strptime(str(time.strftime(OE_DFORMAT)), OE_DFORMAT)
                delta = end - start
                rec.age = parse_date(delta)
            else:
                rec.age = ''

    # This Function is used in the Cron Job daily/weekly/monthly for Age Calculation
    @api.model
    def calculate_age_cron(self):
        today = date.today()
        employees = self.env['hr.employee'].search([])
        if employees:
            for employee in employees:
                if employee.birthday:
                    age2 = today.year - employee.birthday.year - ((today.month, today.day) < (employee.birthday.month, employee.birthday.day))
                    employee.age2 = age2
                else:
                    employee.age2 = 0

    @api.constrains('cnic')
    def _check_cnic(self):
        for rec in self:
            if rec.cnic:
                cnic_com = re.compile('^[0-9+]{5}-[0-9+]{7}-[0-9]{1}$')
                a = cnic_com.search(rec.cnic)
                if a:
                    return True
                else:
                    raise UserError(_("CNIC Format is Incorrect. Format Should like this 00000-0000000-0"))

    @api.model
    def employee_contract_generation(self, nlimit=10):
        recs = self.env['hr.employee'].search([('to_be', '=', True)], limit=nlimit)
        for rec in recs:
            allowances = False
            deductions = False
            contract_vals = ({
                'name': rec.name + " Contract -1",
                'employee_id': rec.id,
                'department_id': rec.department_id and rec.department_id.id or False,
                'state': 'draft',
                'company_id': 1,
                'type_id': 1,
                'struct_id': 1,
                'date_start': '2021-07-01',
                'new_date_start': '2021-07-01',
                'wage': 0.0,
            })
            contract_id = self.env['hr.contract'].create(contract_vals)
            allowances = self.env['allowances.fixation'].search([('code', '=', rec.code), ('to_be', '=', True)])
            deductions = self.env['deductions.fixation'].search([('code', '=', rec.code), ('to_be', '=', True)])

            # Allowances
            if allowances:
                for allowance in allowances:
                    if allowance.head_name_detail=='Basic Pay':
                        contract_id.wage = allowance.allowance_amount
                        allowance.to_be = False
                    else:
                        salary_allowance = False
                        type_id = allowance.percentage_type_id + 11
                        salary_allowance = self.env['hr.salary.allowances'].search(
                            [('name', '=', allowance.head_name_detail),
                             ('percentage', '=', allowance.head_by_percentage), ('percentage_type_id', '=', type_id)])
                        if salary_allowance:
                            salary_allowance = salary_allowance[0]
                            allow_vals = ({
                                'contract_id': contract_id.id,
                                'employee_id': rec.id,
                                'allowance_id': salary_allowance.id,
                                'amount': allowance.allowance_amount,
                            })
                            new_allow_rec = self.env['hr.emp.salary.allowances'].create(allow_vals)
                            new_allow_rec.to_be = False

            # Deductions
            if deductions:
                for deduction in deductions:
                    salary_deduction = False
                    type_id = deduction.percentage_type_id + 11
                    salary_deduction = self.env['hr.salary.deductions'].search(
                        [('name', '=', deduction.head_name_detail), ('percentage', '=', deduction.head_by_percentage),
                         ('percentage_type_id', '=', type_id)])
                    if salary_deduction:
                        salary_deduction = salary_deduction[0]
                        deduct_vals = ({
                            'contract_id': contract_id.id,
                            'employee_id': rec.id,
                            'allowance_id': salary_deduction.id,
                            'amount': deduction.allowance_amount,
                        })
                        new_deduct_rec = self.env['hr.emp.salary.deductions'].create(deduct_vals)
                        new_deduct_rec.to_be = False

            if contract_id:
                rec.to_be = False
                _logger.info('.......Contract for the Employee %r generated . ..............', contract_id.employee_id.name)

    @api.depends('slip_ids', 'contract_ids', 'contract_ids.date_start')
    def get_salary_comp(self):
        for emp in self:
            gross = emp.manual_gross
            tax = emp.manual_tax

            config_fy_start = self.env['ir.config_parameter'].sudo().get_param('aarsol_hr.fiscal_year_start')
            fy_start = fields.Date.from_string(config_fy_start or '2019-07-01')
            slips = emp.slip_ids.filtered(lambda l: l.state=='done' and l.date_from >= fy_start)
            for slip in slips:
                gross_line = slip.line_ids.filtered(lambda l: l.salary_rule_id.code=='GROSS')
                if gross_line:
                    gross += gross_line.total
                tax_line = slip.line_ids.filtered(lambda l: l.salary_rule_id.code=='IT')
                if tax_line:
                    tax += abs(tax_line.total)

            emp.gross_salary = gross
            emp.tax_deducted = tax

            if emp.contract_ids:
                config_fy_end = self.env['ir.config_parameter'].sudo().get_param('aarsol_hr.fiscal_year_end')
                fy_end = fields.Date.from_string(config_fy_end or '2020-06-30')
                # last_date = datetime.strptime('2020-06-30', '%Y-%m-%d').date()
                contract_date = fields.Date.from_string(emp.contract_ids[0].date_start)
                months = min(round(((fy_end - contract_date).days) / 30), 12)
                # months = 12
                rem_slips = months - len(slips) - emp.manual_slips
                future_salary = (rem_slips - 1) * emp.contract_ids[0].wage
                emp.future_salary = future_salary
                emp.rem_slips = rem_slips

    @api.depends('birthday')
    def _compute_retirement_date(self):
        for rec in self:
            retirement_period = int(self.env['ir.config_parameter'].sudo().get_param('aarsol_hr_ext.retirement_period') or '60')
            if rec.birthday:
                rec.retirement_date = rec.birthday + relativedelta(years=retirement_period, days=-1)

    def _compute_total_service(self):
        for rec in self:
            if rec.joining_date:
                start = datetime.strptime(str(rec.joining_date), OE_DFORMAT)
                end = datetime.strptime(str(time.strftime(OE_DFORMAT)), OE_DFORMAT)
                delta = end - start
                rec.total_service = parse_date(delta)
            else:
                rec.total_service = ''

    @api.depends('age2')
    def _calc_charge_eobi(self):
        for rec in self:
            if rec.gender=='male':
                if int(rec.age2) < 60:
                    rec.charge_eobi = True
                else:
                    rec.charge_eobi = False
                    employee_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id),
                                                                        ('state', '=', 'open')
                                                                        ], order='id desc', limit=1)
                    if not employee_contract:
                        employee_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id)], order='id desc', limit=1)
                    if employee_contract:
                        # if not employee_contract:
                        #     raise UserError(_("No Contract found for this Employee %s-%s. Please Check it.") % (rec.code, rec.name))
                        if employee_contract.deduction_ids:
                            employee_eobi_deduction = employee_contract.deduction_ids.filtered(lambda deduct: deduct.deduction_id.code=='EOBI')
                            if employee_eobi_deduction:
                                employee_eobi_deduction.expiry_amount = employee_eobi_deduction.amount
                                employee_eobi_deduction.expired = True
                                employee_eobi_deduction.expiry_date = fields.Date.today()

            if rec.gender=='female':
                if int(rec.age2) < 55:
                    rec.charge_eobi = True
                else:
                    rec.charge_eobi = False
                    employee_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id),
                                                                        ('state', '=', 'open')
                                                                        ], order='id desc', limit=1)
                    if not employee_contract:
                        employee_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id)], order='id desc', limit=1)
                    # if not employee_contract:
                    #     raise UserError(_("No Contract found for this Employee %s-%s. Please Check it.") % (rec.code, rec.name))
                    if employee_contract:
                        employee_eobi_deduction = employee_contract.deduction_ids.filtered(lambda deduct: deduct.deduction_id.code=='EOBI')
                        if employee_eobi_deduction:
                            employee_eobi_deduction.expiry_amount = employee_eobi_deduction.amount
                            employee_eobi_deduction.expired = True
                            employee_eobi_deduction.expiry_date = fields.Date.today()

    def action_profile_lock(self):
        for rec in self:
            rec.profile_state = 'lock'

    def action_profile_unlock(self):
        for rec in self:
            rec.profile_state = 'draft'

    # Broken Periods for Half Pay leaves
    def get_half_pay_calc(self, payslip_id=None, payslip_amount=0, total_days=0, conveyance=False):
        if payslip_id is not None and payslip_amount > 0 and total_days > 0:
            amount = 0
            if payslip_id.date_from < self.half_pay_leave_start_date < payslip_id.date_to:
                if conveyance:
                    full_pay_days = (self.half_pay_leave_start_date - payslip_id.date_from).days
                    amount = ((payslip_amount / total_days) * full_pay_days) / total_days
                else:
                    full_pay_days = (self.half_pay_leave_start_date - payslip_id.date_from).days
                    full_day_amount = (payslip_amount / total_days) * full_pay_days
                    half_pay_days = (payslip_id.date_to - self.half_pay_leave_start_date).days + 1
                    half_day_amount = ((payslip_amount / total_days) * half_pay_days) / 2
                    amount = (full_day_amount + half_day_amount) / total_days

            elif payslip_id.date_from < self.half_pay_leave_end_date < payslip_id.date_to:
                if conveyance:
                    full_pay_days = (payslip_id.date_to - self.half_pay_leave_end_date).days
                    amount = ((payslip_amount / total_days) * full_pay_days) / total_days
                else:
                    half_pay_days = (self.half_pay_leave_end_date - payslip_id.date_from).days + 1
                    half_day_amount = ((payslip_amount / total_days) * half_pay_days) / 2
                    full_pay_days = (payslip_id.date_to - self.half_pay_leave_end_date).days
                    full_day_amount = (payslip_amount / total_days) * full_pay_days
                    amount = (full_day_amount + half_day_amount) / total_days

            else:
                if conveyance:
                    amount = 0
                else:
                    amount = (payslip_amount / total_days) / 2
            return amount

    @api.onchange('basic_pay_type')
    def onchange_base_pay_type(self):
        for rec in self:
            rec.payscale_category = False
            rec.payscale_id = False
            rec.stage = 0

    @api.onchange('payscale_category')
    def onchange_payscale_category(self):
        for rec in self:
            rec.payscale_id = False

    @api.constrains('stage')
    def payscale_stage_constrains(self):
        for rec in self:
            if rec.payscale_id:
                if rec.stage > rec.payscale_id.stages:
                    raise ValidationError(_('❌ Employee Stage should be Less than or Equal to Payscale Stages.\n❌ Last Stage of specified Payscale is %s and you have entered %s', rec.payscale_id.stages, rec.stage))

    @api.onchange('payscale_id', 'stage')
    def onchange_payscale_id(self):
        for rec in self:
            employee_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id),
                                                                ('state', '=', 'open')], order='id desc', limit=1)
            if not employee_contract:
                employee_contract = self.env['hr.contract'].search([('employee_id', '=', rec._origin.id),
                                                                    ('state', '=', 'open')], order='id desc', limit=1)
            if employee_contract:
                employee_contract.payscale_id = rec.payscale_id.id
                employee_contract.stage = rec.stage

    @api.model
    def employee_retirement_cron(self):
        employee_list = self.env['hr.employee'].search([('retirement_date', '<=', fields.Date.today()),
                                                        ('state', '=', 'active'),
                                                        ('re_appointed', '!=', True)])
        if employee_list:
            for employee in employee_list:
                # Close the Retired Employee Contracts
                contracts = self.env['hr.contract'].search([('employee_id', '=', employee.id),
                                                            ('state', 'in', ('draft', 'open'))])
                if contracts:
                    contracts.write({'state': 'close',
                                     'date_end': employee.retirement_date})

                # Create Record in the Employee Status History
                history_data_values = {
                    'employee_id': employee.id,
                    'department_id': employee.department_id and employee.department_id.id or False,
                    'designation_id': employee.job_id and employee.job_id.id or False,
                    'date': fields.Date.today(),
                    'old_status': employee.state,
                    'new_status': 'retired',
                    'state': 'lock',
                }
                new_history_rec = self.env['hr.employee.status.history'].create(history_data_values)

                # Change Employee Status to Retired
                employee.write({'state': 'retired',
                                'retired': True})


class HRContract(models.Model):
    _inherit = 'hr.contract'

    allowance_ids = fields.One2many('hr.emp.salary.allowances', 'contract_id', 'Allowances', domain=[('expired', '=', False)])
    deduction_ids = fields.One2many('hr.emp.salary.deductions', 'contract_id', 'Deductions', domain=[('expired', '=', False)])

    expired_allowance_ids = fields.One2many('hr.emp.salary.allowances', 'contract_id', 'Expired Allowances', domain=[('expired', '=', True)])
    expired_deduction_ids = fields.One2many('hr.emp.salary.deductions', 'contract_id', 'Expired Deductions', domain=[('expired', '=', True)])

    payscale_id = fields.Many2one('hr.payscale', string='Payscale', compute='_compute_payscale', store=True)
    stage = fields.Integer(string='Stage', compute='_compute_payscale', store=True)
    basic_pay = fields.Integer(compute='_compute_basic_pay', string='Basic Pay')
    basic_pay_initial = fields.Integer(compute='_compute_basic_pay', string='Initial Basic Pay')
    match_pay = fields.Boolean(string="Match", default=False)
    basic_pay_type = fields.Selection(related='employee_id.basic_pay_type', string='Basic Pay Type', store=True)
    wage = fields.Float('Basic Pay', compute='_compute_wage', store=True, readonly=False)

    monetization_amount = fields.Float('Monetization Allowance', compute='_compute_allowances_amount', store=True)
    allowances_amount = fields.Float('Allowances Amount', compute='_compute_allowances_amount', store=True)
    deductions_amount = fields.Float('Deductions Amount', compute='_compute_deductions_amount', store=True)
    gross_salary = fields.Float('Gross Salary', compute="_compute_gross_salary", store=True)
    gross_salary_with_monetization = fields.Float('Gross Salary With Monetization', compute="_compute_gross_salary", store=True)

    net_salary = fields.Float('Net Salary', compute="_compute_net_salary", store=True)

    allowance_template_id = fields.Many2one('hr.salary.allowances.template', 'Allowance Template', tracking=True, compute='_compute_templates', store=True)
    deduction_template_id = fields.Many2one('hr.salary.deductions.template', 'Deduction Template', tracking=True, compute='_compute_templates', store=True)
    personal_pay_amount = fields.Float('Personal Pay Amount')

    # Old Field for Label Change
    date_start = fields.Date('Contract Start Date', required=True, default=fields.Date.today, tracking=True, help="Start date of the contract.")

    # This field store the New Contract Start Date
    # Suppose a contract ends 19-03-2021 and next starts from 20-03-2021, here new_date_start=20-03-2021
    # And (old field) date_start=01-04-2021
    new_date_start = fields.Date('Contract New Start Date', default=fields.Date.today())
    # this is computed variable store whether arrears deductions computed or not of this contract
    arrears_deduction_computed = fields.Boolean('Arrears Deduction Computed')
    show_compute_arrears_button = fields.Boolean('Show Compute Arrears Button', compute='_compute_show_arrears_button', store=True)

    @api.depends('employee_id')
    def _compute_payscale(self):
        for rec in self:
            if rec.employee_id:
                rec.payscale_id = rec.employee_id.payscale_id and rec.employee_id.payscale_id.id or False
                rec.stage = rec.employee_id.stage and rec.employee_id.stage or 0

    def _compute_basic_pay(self):
        for rec in self:
            search_pay_scale = self.env['hr.payscale.category'].search([('active', '=', True),
                                                                        ('id', '=', rec.employee_id.payscale_category.id)
                                                                        ], order='id desc', limit=1)
            pay_scale = search_pay_scale.scale_ids.filtered(lambda l: l.name==rec.payscale_id.name)
            rec.basic_pay = pay_scale.basic_pay + float(rec.stage) * pay_scale.increment
            rec.basic_pay_initial = pay_scale.basic_pay
            if rec.basic_pay==rec.wage:
                rec.match_pay = True
            else:
                rec.match_pay = False

    @api.depends('employee_id.payscale_category', 'employee_id.payscale_id', 'employee_id.stage', 'employee_id.basic_pay_type')
    def _compute_wage(self):
        for rec in self:
            if rec.state not in ('close', 'cancel'):
                if rec.employee_id.basic_pay_type=='scale_base':
                    search_pay_scale = self.env['hr.payscale.category'].search([('active', '=', True),
                                                                                ('id', '=', rec.employee_id.payscale_category.id)
                                                                                ], order='id desc', limit=1)
                    pay_scale = search_pay_scale.scale_ids.filtered(lambda l: l.name==rec.payscale_id.name)
                    rec.wage = pay_scale.basic_pay + float(rec.stage) * pay_scale.increment

    @api.onchange('employee_id')
    def new_onchange_employee(self):
        if self.employee_id:
            contracts = self.search_count([('employee_id', '=', self.employee_id.id)])
            contracts += 1
            self.name = 'EM.' + str(self.employee_id.code) + '-' + str(contracts)

    @api.depends('allowance_ids', 'allowance_ids.amount', 'allowance_ids.amount_fixed', 'allowance_ids.type')
    def _compute_allowances_amount(self):
        for rec in self:
            amt = 0
            mont_alw = 0
            rec.flush()
            if rec.allowance_ids:
                for alw in rec.allowance_ids:
                    amt += alw.amount if not alw.allowance_id.special_flag else 0
                    mont_alw += alw.amount if alw.allowance_id.special_flag else 0
            rec.allowances_amount = round(amt)
            rec.monetization_amount = round(mont_alw)

    @api.depends('deduction_ids', 'deduction_ids.amount', 'deduction_ids.amount_fixed', 'deduction_ids.type')
    def _compute_deductions_amount(self):
        for rec in self:
            self.env['hr.emp.salary.deductions'].flush(['amount'])
            amt = 0
            if rec.deduction_ids:
                for deduct in rec.deduction_ids:
                    amt += deduct.amount
            rec.deductions_amount = round(amt)

    @api.depends('wage', 'allowances_amount', 'personal_pay_amount')
    def _compute_gross_salary(self):
        for rec in self:
            rec.gross_salary = rec.wage + rec.allowances_amount + rec.personal_pay_amount
            rec.gross_salary_with_monetization = rec.wage + rec.allowances_amount + rec.monetization_amount + rec.personal_pay_amount

    @api.depends('wage', 'allowances_amount', 'deductions_amount', 'personal_pay_amount')
    def _compute_net_salary(self):
        for rec in self:
            rec.net_salary = rec.wage + rec.allowances_amount + rec.personal_pay_amount + rec.monetization_amount - rec.deductions_amount

    def _get_work_hours(self, date_from, date_to, domain=None):
        """
        Returns the amount (expressed in hours) of work
        for a contract between two dates.
        If called on multiple contracts, sum work amounts of each contract.
        :param date_from: The start date
        :param date_to: The end date
        :returns: a dictionary {work_entry_id: hours_1, work_entry_2: hours_2}
        """
        generated_date_max = min(fields.Date.to_date(date_to), date_utils.end_of(fields.Date.today(), 'month'))
        self._generate_work_entries(date_from, generated_date_max)
        date_from = datetime.combine(date_from, datetime.min.time())
        date_to = datetime.combine(date_to, datetime.max.time())
        work_data = defaultdict(int)

        # First, found work entry that didn't exceed interval.
        work_entries = self.env['hr.work.entry'].read_group(
            self._get_work_hours_domain(date_from, date_to, domain=domain, inside=True),
            ['hours:sum(duration)'],
            ['work_entry_type_id']
        )
        work_data.update({data['work_entry_type_id'][0] if data['work_entry_type_id'] else False: data['hours'] for data in work_entries})

        # Second, find work entry that exceeds interval and compute right duration.
        work_entries = self.env['hr.work.entry'].search(self._get_work_hours_domain(date_from, date_to, domain=domain, inside=False))

        for work_entry in work_entries:
            date_start = max(date_from, work_entry.date_start)
            date_stop = min(date_to, work_entry.date_stop)
            if work_entry.work_entry_type_id.is_leave:
                contract = work_entry.contract_id
                calendar = contract.resource_calendar_id
                employee = contract.employee_id
                contract_data = employee._get_work_days_data_batch(
                    date_start, date_stop, compute_leaves=False, calendar=calendar
                )[employee.id]

                work_data[work_entry.work_entry_type_id.id] += contract_data.get('hours', 0)
            else:
                dt = date_stop - date_start
                work_data[work_entry.work_entry_type_id.id] += dt.days * 24 + dt.seconds / 3600  # Number of hours
        return work_data

    @api.depends('employee_id')
    def _compute_templates(self):
        for rec in self:
            if rec.employee_id:
                rec.allowance_template_id = rec.employee_id.allowance_template_id and rec.employee_id.allowance_template_id.id or False
                rec.deduction_template_id = rec.employee_id.deduction_template_id and rec.employee_id.deduction_template_id.id or False

    @api.model
    def create(self, vals):
        prev_contract = False
        if vals.get('employee_id', False):
            prev_contract = self.env['hr.contract'].search([('employee_id', '=', vals['employee_id'])], order='id desc', limit=1)
            if prev_contract:
                vals['adhoc_allowance_2016'] = prev_contract.adhoc_allowance_2016
            employee_rec = self.env['hr.employee'].search([('id', '=', vals['employee_id'])])
            if employee_rec and not employee_rec.state=='active':
                raise UserError(_('Active State Employee Contract can be create. \nEmployee %s is not in the Active State') % (employee_rec.name))

        contracts = super(HRContract, self).create(vals)
        for contract in contracts:
            # Update Personal Pay
            if contract.employee_id.personal_pay_count > 0:
                contract.personal_pay_amount = contract.employee_id.personal_pay_count * contract.payscale_id.increment

            if contract.allowance_template_id and contract.allowance_template_id.template_lines:
                for line in contract.allowance_template_id.template_lines:
                    salary_percentage_id = False
                    alw_flag = False
                    if line.percentage_ids:
                        for ap_line in line.percentage_ids:
                            if ap_line.domain:
                                if self.env['hr.employee'].search(safe_eval(ap_line.domain) + [('id', '=', contract.employee_id.id)]):
                                    alw_flag = True
                                    salary_percentage_id = ap_line
                            if not alw_flag and not ap_line.domain and ap_line.value > 0:
                                alw_flag = True
                    if alw_flag:
                        allowance_values = {
                            'contract_id': contract.id,
                            'employee_id': contract.employee_id.id,
                            'allowance_id': line.id,
                            'payscale_id': contract.employee_id.payscale_id and contract.employee_id.payscale_id.id or False,
                            'salary_percentage_id': salary_percentage_id and salary_percentage_id.id or False,
                        }
                        new_allowance_rec = self.env['hr.emp.salary.allowances'].create(allowance_values)

            if contract.deduction_template_id and contract.deduction_template_id.template_lines:
                for line in contract.deduction_template_id.template_lines:
                    salary_percentage_id = False
                    dd_flag = False
                    if line.percentage_ids:
                        for dp_line in line.percentage_ids:
                            if dp_line.domain:
                                if self.env['hr.employee'].search(safe_eval(dp_line.domain) + [('id', '=', contract.employee_id.id)]):
                                    dd_flag = True
                                    salary_percentage_id = dp_line
                            if not dd_flag and not dp_line.domain and dp_line.value > 0:
                                dd_flag = True
                    if dd_flag:
                        deduction_values = {
                            'contract_id': contract.id,
                            'employee_id': contract.employee_id.id,
                            'deduction_id': line.id,
                            'payscale_id': contract.employee_id.payscale_id and contract.employee_id.payscale_id.id or False,
                            'salary_percentage_id': salary_percentage_id and salary_percentage_id.id or False,
                        }
                        new_deduction_rec = self.env['hr.emp.salary.deductions'].create(deduction_values)
        return contracts

    def action_compute_arrears_deductions(self):
        for contract in self:
            arrears_amount = 0
            deduction_dict = {}
            input_dict = {}

            loan_lines = self.env['hr.loan.line']
            last_payslip = self.env['hr.payslip'].search([('employee_id', '=', contract.employee_id.id),
                                                          ('state', '!=', 'cancel'),
                                                          ('date_from', '<', contract.date_start)
                                                          ], order='id desc', limit=1)
            for d in contract.deduction_ids:
                deduction_dict[str(d.deduction_id.id)] = 0
                deduction_dict[d.deduction_id.name] = d.deduction_id.id

            loans_dict_recs = self.env['hr.loan'].search([('employee_id', '=', contract.employee_id.id)])
            for inp in loans_dict_recs:
                input_dict[str(inp.id)] = 0
                input_dict[inp.name] = inp.id

            # Assuming Swap Variable start_date and new_start_date
            if last_payslip:
                # if contract start (promotion or increment is done) after last month Salary Slip End Date
                # e.g if new contract start date is 10-june-2021 and last month salary slip end date is 31-05-2021
                # Here i should consider the days between last payslip end date and new contract start date
                # days = new contract start data - last payslip end date
                if last_payslip.date_to < contract.date_start:
                    prev_flag = True
                    # Variable to check that if office order is approved or received after or mor than 30 days gap
                    # if diff is more than 30 days then treatment will be totally different
                    overall_days_diff = (contract.new_date_start - contract.date_start).days
                    # days = ((contract.date_start - last_payslip.date_to).days - 1)

                    days = (last_payslip.contract_id.date_end - last_payslip.date_to).days
                    start_dt = last_payslip.date_to
                    if days > 0 and not contract.arrears_deduction_computed:
                        while start_dt < contract.new_date_start:
                            if not prev_flag:
                                month_last_date = start_dt + relativedelta(day=31)
                                if month_last_date < contract.new_date_start:
                                    month_last_date = contract.new_date_start
                                days = (month_last_date - start_dt).days
                                if days > 0:
                                    month_days = start_dt + relativedelta(day=31)
                                    month_days = month_days.day
                                    wage = ((contract.wage / month_days) * days)
                                    allowances_amount = ((contract.allowances_amount / month_days) * days)
                                    mon_allowance = ((contract.monetization_amount / month_days) * days)
                                    personal_pay_amount = ((contract.personal_pay_amount / month_days) * days)
                                    adhoc_2016_amount = ((contract.adhoc_allowance_2016 / month_days) * days)
                                    arrears_amount = arrears_amount + wage + allowances_amount + mon_allowance + personal_pay_amount + adhoc_2016_amount

                                    loans = self.env['hr.loan.line'].search([('employee_id', '=', contract.employee_id.id),
                                                                             ('paid_date', '>=', start_dt + relativedelta(day=1)),
                                                                             ('paid_date', '<=', month_last_date),
                                                                             ('paid', '=', False)])
                                    if loans:
                                        loan_lines += loans
                                    # for loan in loans:
                                    #     input_dict[str(loan.loan_id.id)] += ((loan.paid_amount / month_days) * days)
                                    for deduction in contract.deduction_ids:
                                        deduction_dict[str(deduction.deduction_id.id)] += (deduction.amount / month_days) * days
                                    start_dt += relativedelta(months=1, day=1)

                            # This If Condition Will Run for every One (Only One Time)
                            if prev_flag:
                                start_dt = contract.date_start
                                month_last_date = start_dt + relativedelta(day=31)
                                month_days = month_last_date.day
                                prev_flag = False
                                prev_contract = last_payslip.contract_id
                                if prev_contract:
                                    arrears_date = contract.date_start
                                    expired_allowances_amount = 0
                                    wage = ((prev_contract.wage / month_days) * days)
                                    mon_allowance = ((prev_contract.monetization_amount / month_days) * days)
                                    personal_pay_amount = ((prev_contract.personal_pay_amount / month_days) * days)
                                    adhoc_2016_amount = ((prev_contract.adhoc_allowance_2016 / month_days) * days)

                                    for prev_alw in prev_contract.expired_allowance_ids:
                                        expired_allowances_amount += prev_alw.amount
                                    allowances_amount = ((expired_allowances_amount / month_days) * days)
                                    arrears_amount = arrears_amount + wage + allowances_amount + mon_allowance + personal_pay_amount + adhoc_2016_amount

                                    loans = self.env['hr.loan.line'].search([('employee_id', '=', contract.employee_id.id),
                                                                             ('paid_date', '>=', start_dt + relativedelta(day=1)),
                                                                             ('paid_date', '<=', month_last_date),
                                                                             ('paid', '=', False)])
                                    # for loan in loans:
                                    #     input_dict[str(loan.loan_id.id)] += ((loan.paid_amount / month_days) * days)

                                    for deduction in prev_contract.expired_deduction_ids:
                                        deduction_dict[str(deduction.deduction_id.id)] += (deduction.amount / month_days) * days

                                    # Handling remaining Days with New Contract
                                    aabb = start_dt + relativedelta(day=31)
                                    if overall_days_diff >= aabb.day:
                                        arrears_date = contract.new_date_start
                                        days = month_days - days
                                        wage = ((contract.wage / month_days) * days)
                                        allowances_amount = ((contract.allowances_amount / month_days) * days)
                                        mon_allowance = ((contract.monetization_amount / month_days) * days)
                                        personal_pay_amount = ((contract.personal_pay_amount / month_days) * days)
                                        adhoc_2016_amount = ((contract.adhoc_allowance_2016 / month_days) * days)
                                        arrears_amount = arrears_amount + wage + allowances_amount + mon_allowance + personal_pay_amount + adhoc_2016_amount

                                        loans = self.env['hr.loan.line'].search([('employee_id', '=', contract.employee_id.id),
                                                                                 ('paid_date', '>=', start_dt + relativedelta(day=1)),
                                                                                 ('paid_date', '<=', month_last_date),
                                                                                 ('paid', '=', False)])
                                        for loan in loans:
                                            # input_dict[str(loan.loan_id.id)] += ((loan.paid_amount / month_days) * days)
                                            input_dict[str(loan.loan_id.id)] += loan.paid_amount
                                            loan.paid = True
                                        for deduction in prev_contract.expired_deduction_ids:
                                            deduction_dict[str(deduction.deduction_id.id)] += (deduction.amount / month_days) * days
                                    start_dt += relativedelta(months=1, day=1)

                # If contract is created before the last month salary slip End Date
                if last_payslip.date_to >= contract.date_start:
                    arrears_date = contract.new_date_start
                    days = (last_payslip.date_to - contract.date_start).days + 1
                    start_dt = contract.date_start

                    if days > 0:
                        h_flag = False
                        while start_dt < contract.new_date_start:
                            month_last_date = start_dt + relativedelta(day=31)
                            month_days = month_last_date.day
                            if h_flag:
                                if month_last_date > contract.new_date_start:
                                    days = (contract.new_date_start - start_dt).days + 1
                                else:
                                    days = month_days

                            wage = ((contract.wage / month_days) * days)
                            allowances_amount = ((contract.allowances_amount / month_days) * days)
                            mon_allowance = ((contract.monetization_amount / month_days) * days)
                            personal_pay_amount = ((contract.personal_pay_amount / month_days) * days)
                            adhoc_2016_amount = ((contract.adhoc_allowance_2016 / month_days) * days)
                            arrears_amount = arrears_amount + wage + allowances_amount + mon_allowance + personal_pay_amount + adhoc_2016_amount

                            loans = self.env['hr.loan.line'].search([('employee_id', '=', contract.employee_id.id),
                                                                     ('paid_date', '>=', start_dt + relativedelta(day=1)),
                                                                     ('paid_date', '<=', month_last_date),
                                                                     ('paid', '=', False)])
                            if loans:
                                loan_lines += loans
                            # for loan in loans:
                            #     input_dict[str(loan.loan_id.id)] += ((loan.paid_amount / month_days) * days)
                            for deduction in contract.deduction_ids:
                                deduction_dict[str(deduction.deduction_id.id)] += (deduction.amount / month_days) * days
                            start_dt += relativedelta(months=1, day=1)
                            h_flag = True

            # It its new Contract
            if not last_payslip:
                if contract.new_date_start > contract.date_start:
                    start_dt = contract.date_start
                    arrears_date = contract.new_date_start
                    days = (contract.date_start + relativedelta(day=31) - contract.date_start).days + 1
                    if days > 0 and not contract.arrears_deduction_computed:
                        while start_dt < contract.new_date_start:
                            month_last_date = start_dt + relativedelta(day=31)
                            if month_last_date > contract.new_date_start:
                                month_last_date = contract.new_date_start
                            days = (month_last_date - start_dt).days + 1
                            if days > 0:
                                month_days = start_dt + relativedelta(day=31)
                                month_days = month_days.day
                                wage = ((contract.wage / month_days) * days)
                                allowances_amount = ((contract.allowances_amount / month_days) * days)
                                mon_allowance = ((contract.monetization_amount / month_days) * days)
                                personal_pay_amount = ((contract.personal_pay_amount / month_days) * days)
                                adhoc_2016_amount = ((contract.adhoc_allowance_2016 / month_days) * days)
                                arrears_amount = arrears_amount + wage + allowances_amount + mon_allowance + personal_pay_amount + adhoc_2016_amount

                                loans = self.env['hr.loan.line'].search([('employee_id', '=', contract.employee_id.id),
                                                                         ('paid_date', '>=', start_dt + relativedelta(day=1)),
                                                                         ('paid_date', '<=', month_last_date),
                                                                         ('paid', '=', False)])
                                if loans:
                                    loan_lines += loans
                                for deduction in contract.deduction_ids:
                                    deduction_dict[str(deduction.deduction_id.id)] += (deduction.amount / month_days) * days
                                start_dt += relativedelta(months=1, day=1)

            if len(deduction_dict):
                for d_dict in deduction_dict.items():
                    salary_structure_id = 1
                    if contract.employee_id.employee_category=='Education':
                        salary_structure_id = 2
                    deduct_rec = self.env['hr.salary.deductions'].search([('name', '=', d_dict[0]), ('rule_ids.salary_structure_id', '=', salary_structure_id)])
                    if deduct_rec:
                        bba_values = {
                            'employee_id': contract.employee_id.id,
                            'employee_code': contract.employee_id.code and contract.employee_id.code or '',
                            'department_id': contract.employee_id.department_id and contract.employee_id.department_id.id or False,
                            'job_id': contract.employee_id.job_id and contract.employee_id.job_id.id or False,
                            'contract_id': contract and contract.id or False,
                            'date_from': arrears_date,
                            # 'date_to': start_dt,
                            # 'date_from': last_payslip.contract_id.date_end,
                            'date_to': last_payslip.contract_id.date_end,
                            'slip_month': arrears_date,
                            'date': fields.Date.today(),
                            'ttype': 'deduction',
                            'allowance_ids': [],
                            'deduction_ids': [[6, 0, deduct_rec.ids]],
                            'state': 'draft',
                            'calculation_type': 'New',
                            'total_amount': int(deduction_dict[str(d_dict[1])]),
                            'amount': int(deduction_dict[str(d_dict[1])]),
                            'skip_calculation': True,
                        }
                        new_rec = self.env['hr.employee.backdate.arrears'].create(bba_values)
                        new_rec.state = 'confirm'

            # if len(input_dict):
            #     for in_dict in input_dict.items():
            #         emp_loan_rec = self.env['hr.loan'].search([('name', '=', in_dict[0])])
            #         rule_input_id = self.env['hr.salary.inputs'].search([('salary_rule_id', '=', emp_loan_rec.loan_id.salary_rule_id.id)])
            #         if emp_loan_rec:
            #             bp_input_id = self.env['hr.emp.salary.inputs'].create({
            #                 'employee_id': contract.employee_id.id,
            #                 'name': 'LOAN',
            #                 'amount': int(input_dict[str(in_dict[1])]),
            #                 'state': 'confirm',
            #                 'input_id': rule_input_id and rule_input_id.id or False,
            #                 'date': arrears_date,
            #             })

            if loan_lines:
                for loan_line in loan_lines:
                    if loan_line.salary_input_id and not loan_line.salary_input_id.slip_id:
                        loan_line.paid = True
                        loan_line.salary_input_id.date = arrears_date
                    if loan_line.interest_salary_input_id and not loan_line.interest_salary_input_id.slip_id:
                        loan_line.interest_salary_input_id.date = arrears_date

            if arrears_amount > 0:
                input_id = self.env['ir.config_parameter'].sudo().get_param('aarsol_hr_ext.arrears_input_rule')
                if not input_id:
                    raise UserError('Please First Configure the Input Type for the Arrears')
                emp_salary_input_id = self.env['hr.emp.salary.inputs'].create({
                    'employee_id': contract.employee_id.id,
                    'name': contract.employee_id.name + "- Arrears",
                    'amount': round(arrears_amount),
                    'state': 'confirm',
                    'input_id': input_id,
                    'date': arrears_date,
                    'description': contract.id,
                })
            contract.arrears_deduction_computed = True

    @api.depends('arrears_deduction_computed', 'date_start', 'new_date_start')
    def _compute_show_arrears_button(self):
        for rec in self:
            flag = False
            if rec.date_start and rec.new_date_start:
                days = (rec.new_date_start - rec.date_start).days
                if days > 0 and not rec.arrears_deduction_computed:
                    flag = True
            rec.show_compute_arrears_button = flag

    # Cron Job, It will set the Employee Allowances and Deductions
    # Salary Percentage ID Required Amount Calculation
    @api.model
    def salary_percentage_id_cron(self):
        recs = self.env['hr.contract'].search([])
        sr = 0
        for rec in recs.with_progress(msg="Contract Processing"):
            sr += 1
            allowance_ids = []
            if rec.allowance_ids:
                for alw in rec.allowance_ids:
                    _logger.info('*** Contract %s', rec.name)
                    if alw.allowance_id:
                        for ap_line in alw.allowance_id.percentage_ids:
                            if ap_line.domain:
                                if self.env['hr.employee'].search(safe_eval(ap_line.domain) + [('id', '=', rec.employee_id.id)]):
                                    alw.salary_percentage_id = ap_line and ap_line.id or False

            if rec.expired_allowance_ids:
                for alw in rec.expired_allowance_ids:
                    _logger.info('*** Expired Contract %s', rec.name)
                    if alw.allowance_id:
                        for ap_line in alw.allowance_id.percentage_ids:
                            if ap_line.domain:
                                if self.env['hr.employee'].search(safe_eval(ap_line.domain) + [('id', '=', rec.employee_id.id)]):
                                    alw.salary_percentage_id = ap_line and ap_line.id or False

            if rec.deduction_ids:
                for ded in rec.deduction_ids:
                    _logger.info('*** Contract Deduction %s', rec.name)
                    if ded.deduction_id:
                        for ded_line in ded.deduction_id.percentage_ids:
                            if ded_line.domain:
                                if self.env['hr.employee'].search(safe_eval(ded_line.domain) + [('id', '=', rec.employee_id.id)]):
                                    ded.salary_percentage_id = ded_line and ded_line.id or False

            if rec.expired_deduction_ids:
                for ded in rec.expired_deduction_ids:
                    _logger.info('***Expired Contract Deduction %s', rec.name)
                    if ded.deduction_id:
                        for ded_line in ded.deduction_id.percentage_ids:
                            if ded_line.domain:
                                if self.env['hr.employee'].search(safe_eval(ded_line.domain) + [('id', '=', rec.employee_id.id)]):
                                    ded.salary_percentage_id = ded_line and ded_line.id or False

    # this Function will recompute the Allowances and Deductions, May be you have changed the domain of the Allowance and Deduction
    def recompute_allowances_deductions(self):
        for rec in self:
            if rec.state in ('done', 'cancel'):
                raise UserError(_("This Action cannot Performed on Expired or Cancelled Contract, %s-%s Employee Contract is either Expired or Cancelled") % (rec.employee_id.code, rec.employee_id.name))
            # if not rec.allowance_ids and rec.deduction_ids:
            #     raise UserError(_("No allowances and Deductions Found in the System for this Contract"))
            # for Allowances
            if rec.allowance_ids:
                for alw_id in rec.allowance_ids:
                    if alw_id.allowance_id.percentage_ids:
                        expired_flag = True
                        for percentage_id in alw_id.allowance_id.percentage_ids:
                            if percentage_id.domain:
                                if expired_flag and self.env['hr.employee'].search(safe_eval(percentage_id.domain) + [('id', '=', rec.employee_id.id)]):
                                    if alw_id.salary_percentage_id and alw_id.salary_percentage_id.id==percentage_id.id:
                                        expired_flag = False
                        if expired_flag:
                            alw_id.write({'expired': True, 'expiry_amount': alw_id.amount, 'expiry_date': fields.Date.today()})
            # Add
            if rec.allowance_template_id and rec.allowance_template_id.template_lines:
                contract_alw_percentage_ids = rec.allowance_ids.mapped('salary_percentage_id')
                for line in rec.allowance_template_id.template_lines:
                    salary_percentage_id = False
                    alw_flag = False
                    if line.percentage_ids:
                        for ap_line in line.percentage_ids:
                            if ap_line not in contract_alw_percentage_ids:
                                if ap_line.domain:
                                    if self.env['hr.employee'].search(safe_eval(ap_line.domain) + [('id', '=', rec.employee_id.id)]):
                                        alw_flag = True
                                        salary_percentage_id = ap_line
                                if not alw_flag and not ap_line.domain and ap_line.value > 0:
                                    alw_flag = True
                    if alw_flag:
                        allowance_values = {
                            'contract_id': rec.id,
                            'employee_id': rec.employee_id.id,
                            'allowance_id': line.id,
                            'payscale_id': rec.employee_id.payscale_id and rec.employee_id.payscale_id.id or False,
                            'salary_percentage_id': salary_percentage_id and salary_percentage_id.id or False,
                        }
                        new_allowance_rec = self.env['hr.emp.salary.allowances'].create(allowance_values)

            # for Deductions
            if rec.deduction_ids:
                for deduct_id in rec.deduction_ids:
                    if deduct_id.deduction_id.percentage_ids:
                        expired_flag = True
                        for percentage_id in deduct_id.deduction_id.percentage_ids:
                            if percentage_id.domain:
                                if expired_flag and self.env['hr.employee'].search(safe_eval(percentage_id.domain) + [('id', '=', rec.employee_id.id)]):
                                    if deduct_id.salary_percentage_id and deduct_id.salary_percentage_id.id==percentage_id.id:
                                        expired_flag = False
                        if expired_flag:
                            deduct_id.write({'expired': True, 'expiry_amount': deduct_id.amount, 'expiry_date': fields.Date.today()})

            # Add
            if rec.deduction_template_id and rec.deduction_template_id.template_lines:
                contract_deduct_percentage_ids = rec.deduction_ids.mapped('salary_percentage_id')
                for line in rec.deduction_template_id.template_lines:
                    salary_percentage_id = False
                    dd_flag = False
                    if line.percentage_ids:
                        for dp_line in line.percentage_ids:
                            if dp_line not in contract_deduct_percentage_ids:
                                if dp_line.domain:
                                    if self.env['hr.employee'].search(safe_eval(dp_line.domain) + [('id', '=', rec.employee_id.id)]):
                                        dd_flag = True
                                        salary_percentage_id = dp_line
                                if not dd_flag and not dp_line.domain and dp_line.value > 0:
                                    dd_flag = True
                    if dd_flag:
                        deduction_values = {
                            'contract_id': rec.id,
                            'employee_id': rec.employee_id.id,
                            'deduction_id': line.id,
                            'payscale_id': rec.employee_id.payscale_id and rec.employee_id.payscale_id.id or False,
                            'salary_percentage_id': salary_percentage_id and salary_percentage_id.id or False,
                        }
                        new_deduction_rec = self.env['hr.emp.salary.deductions'].create(deduction_values)


class EmployeeSkill(models.Model):
    _inherit = 'hr.resume.line'

    @api.onchange('date_start', 'date_end')
    def _total_experience_days(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                start = datetime.strptime(str(rec.date_start), OE_DFORMAT)
                end = datetime.strptime(str(rec.date_end), OE_DFORMAT)
                delta = end - start
                rec.total_experience = parse_date(delta)
            else:
                rec.total_experience = ''

    line_type_id = fields.Many2one('hr.resume.line.type', string="Type")
    line_type_name = fields.Char('Type Name', related="line_type_id.name")
    total_experience = fields.Char(compute='_total_experience_days', string="Total Experience", help="Auto Calculated")
    reporting_to = fields.Char("Reporting To")
    reason_to_leave = fields.Text("Reason For Leaving")
    responsibilities = fields.Text("Responsibilities")

    # degree_level = fields.Selection([('under_matric', 'Under Matric'),
    #                                  ('matric', 'Matric'),
    #                                  ('inter', 'Intermediate'),
    #                                  ('undergraduate', 'Graduate'),
    #                                  ('postgraduate', 'Postgraduate'),
    #                                  ('professional_education', 'Professional Education'),
    #                                  ('mphil', 'MPhil'),
    #                                  ('phd', ' phd'),
    #                                  ], 'Degree Level')

    degree_level = fields.Selection(
        [('matric', 'Matric'), ('olevel', 'O Levels'), ('inter', 'Intermediate'), ('alevel', 'A Levels'),
         ('bachelor2year', 'Bachelors 2 Years'), ('bachelor4year', 'Bachelors 4 Years'), ('masters', 'Masters'),
         ('mphil', 'MS/Mphil'), ('phd', 'PhD'), ('postdoc', 'Post.Doc'), ('llb', 'LLB')], 'Degree Level', )

    year = fields.Char('Passing Year')
    board = fields.Char('Board Name')
    subjects = fields.Char('Subjects')
    total_marks = fields.Float('Total Marks/CGPA')
    obtained_marks = fields.Float('Obtained Marks/CGPA')
    degree_verified = fields.Boolean('Degree Verified', default=False)
    domicile = fields.Selection([('ICT', 'ICT'),
                                 ('Punjab', 'Punjab'),
                                 ('Sindh (U)', 'Sindh (U)'),
                                 ('Sindh (R)', 'Sindh (R)'),
                                 ('KPK', 'KPK'),
                                 ('Balochistan', 'Balochistan'),
                                 ('AJK', 'AJK'),
                                 ('GB', 'GB'),
                                 ], string='Domicile')

    institute_name = fields.Char(string="Institute Name")
    city_name = fields.Char(string="City")
    location_id = fields.Many2one('res.country', string="Country")
    job_position = fields.Char(string="Job Position")
    grade = fields.Char(string="Grade/Level")

    organization = fields.Char('Organization')
    certificate_name = fields.Char('Certificate/Diploma')
    approval = fields.Boolean('Approval')
    attachment = fields.Binary('Attachment')
    hec_verification_status = fields.Boolean('HEC Verification Status')


class AllowancesFixation(models.Model):
    _name = 'allowances.fixation'
    _description = 'Allowances Fixations'

    code = fields.Char('Code')
    head_name_detail = fields.Char('Head Name Detail')
    head_id_detail = fields.Char('Head ID Detail')
    head_by_percentage = fields.Float('Head By Percentage')
    percentage_type_id = fields.Integer('Percentage Type')
    allowance_amount = fields.Float('Allowance Amount')
    to_be = fields.Boolean('To Be', default=False)


class DeductionsFixation(models.Model):
    _name = 'deductions.fixation'
    _description = 'Deductions Fixations'

    code = fields.Char('Code')
    head_name_detail = fields.Char('Head Name Detail')
    allowance_amount = fields.Float('Allowance Amount')
    head_id_detail = fields.Char('Head ID Detail')
    head_by_percentage = fields.Float('Head By Percentage')
    percentage_type_id = fields.Integer('Percentage Type')
    to_be = fields.Boolean('To Be', default=False)


class HRDepartment(models.Model):
    _inherit = "hr.department"
    _order = 'code,id'

    @api.depends('code', 'name')
    def _get_dept_name(self):
        for rec in self:
            rec.short_name = (rec.code or '') + ":" + rec.name

    name = fields.Char('Department Name', required=True, translate=True)
    code = fields.Char("Code", size=4)
    abbrev = fields.Char("Abbrev", size=2)
    short_name = fields.Char('Short Name', compute='_get_dept_name', store=True)
    user_ids = fields.Many2many('res.users', 'department_user_rel', 'dept_id', 'user_id', 'Users')


class res_users(models.Model):
    _inherit = 'res.users'

    dept_ids = fields.Many2many('hr.department', 'department_user_rel', 'user_id', 'dept_id', 'Departments')

    def name_get(self):
        result = []
        for record in self:
            name = "%s - %s" % (record.login, record.name)
            result.append((record.id, name))
        return result
