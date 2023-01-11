# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import pdb

import logging

_logger = logging.getLogger(__name__)


class HREmployeeIncomeTax(models.Model):
    _name = "hr.employee.income.tax"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Employee Income Tax'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Employee', tracking=True)
    code = fields.Char('Employee Code', compute="_compute_employee_info", store=True)
    department_id = fields.Many2one('hr.department', 'Department', tracking=True, compute="_compute_employee_info", store=True)
    designation_id = fields.Many2one('hr.job', 'Designation', tracking=True, compute="_compute_employee_info", store=True)
    employee_cnic = fields.Char('CNIC', tracking=True, compute="_compute_employee_info", store=True)

    date_from = fields.Date('From Date', tracking=True)
    date_to = fields.Date('To Date', tracking=True)
    year = fields.Char('Year', tracking=True)
    tax_id = fields.Many2one('hr.income.tax', 'Tax', tracking=True)
    tax_slab_id = fields.Many2one('hr.income.tax.line', 'Tax Slab', tracking=True, compute='_calc_tax_amount', store=True)

    basic_wage = fields.Float('Basic Wage', tracking=True, compute='_compute_employee_info', store=True)
    allowances = fields.Float('Allowances', tracking=True, compute='_compute_employee_info', store=True)
    per_month_gross_pay = fields.Float('Per Month Gross Pay', tracking=True, compute='_compute_employee_info', store=True)
    annual_gross_pay = fields.Float('Taxable Income', compute='_compute_employee_info', store=True)

    installment = fields.Float('Months', compute='_compute_months', store=True)
    total_tax_amount = fields.Float('Total Tax Amount', compute='_calc_tax_amount', store=True)
    state = fields.Selection([('Draft', 'Draft'),
                              ('Done', 'Done')
                              ], string='Status', tracking=True, default='Draft', index=True)
    rebate_rate = fields.Float('Rebate Rate (%)')
    rebate_amt = fields.Float('Rebate Amount', compute='_compute_rebate_amt', store=True)
    payable_tax = fields.Float('Payable Tax', compute='_compute_payable_tax', store=True)
    per_month_tax = fields.Float('Per Month Tax Amount', compute='_compute_payable_tax', store=True)
    total_deducted_amount = fields.Float('Total Deduction', tracking=True)
    remaining_amount = fields.Float('Remaining Amount', compute='_calc_remaining_amount', store=True)
    employee_tax_lines = fields.One2many('hr.employee.income.tax.line', 'employee_tax_id', 'Employee Tax Detail')
    tax_adjustment_lines = fields.One2many('hr.employee.income.tax.adjustment', 'employee_tax_id', 'Adjustments')
    adjustment_amt = fields.Float('Adjustment Amount', compute='_compute_adjustment_amt', store=True)
    remarks = fields.Text('Remarks')

    net_income = fields.Float('Net Income')
    manual_gross = fields.Float('Manual Gross')
    manual_tax = fields.Float('Manual Tax')
    manual_slips = fields.Integer('Manual Slips')
    previous_month_gross = fields.Float('Prev. Month Gross')

    create_from_compute_sheet = fields.Boolean('Create From Compute Sheet', default=False)
    active = fields.Boolean('Active', default=True)
    contract_id = fields.Many2one('hr.contract', 'Contract')

    total_tax_amount2 = fields.Float('Total Tax Amount2', compute='_calc_tax_amount', store=True)
    remaining_tax_payable = fields.Float('Remaining Tax', compute='_calc_remaining_tax', store=True)
    total_deducted_amount2 = fields.Float('Total Deduction2', compute="_calc_total_deduction2", store=True)

    annual_income_adjustment_lines = fields.One2many('hr.employee.annual.income.adjustment', 'employee_tax_id', 'Annual Income Adjustments')
    annual_income_adjustment_amt = fields.Float('Annual Income Adjustment Amount', compute='_compute_annual_income_adjustment_amt', store=True)
    tax_generated_later = fields.Boolean('Tax Generated Later', default=False)

    cpr_no_ids = fields.One2many('hr.employee.tax.cpr.no', 'employee_tax_id', 'CPR Nos')

    @api.constrains('employee_id', 'date_from', 'date_to')
    def check_employee_record_duplicate(self):
        for rec in self:
            if rec.employee_id and rec.date_from and rec.date_to:
                already_exits = self.env['hr.employee.income.tax'].search([('employee_id', '=', rec.employee_id.id),
                                                                           ('date_to', '>=', rec.date_from),
                                                                           ('id', '!=', rec.id)])
                if already_exits:
                    raise UserError(_("Duplicate Record of Employee %s (%s) in Taxes \n"
                                      "In the Same Time Period (%s - %s) is not Allowed.", rec.employee_id.name, rec.employee_id.code, rec.date_from.strftime('%d-%B-%Y'), rec.date_to.strftime('%d-%B-%Y')))

    @api.model
    def create(self, values):
        result = super(HREmployeeIncomeTax, self).create(values)
        if not result.name:
            result.name = result.employee_id.name + "/Tax-" + (result.tax_id.year and result.tax_id.year or '')
        if result.date_to < result.date_from:
            raise UserError('From Date Should be Greater then the To Date')
        if result.date_from==result.date_to:
            raise UserError('Date From And Date To Should be Different')
        if result.employee_id and result.employee_id.rebateCateg=='teaching':
            rebate_rate = (int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.rebate_rate')) or '25')
            result.rebate_rate = rebate_rate
        result._compute_payable_tax()
        result._calc_remaining_amount()
        result._calc_remaining_tax()
        return result

    def write(self, values):
        if values.get('date_from', False):
            if self.date_from:
                if str(self.date_to) < values['date_from']:
                    raise UserError('From Date Should be Greater then the To Date')
                if str(self.date_to)==values['date_from']:
                    raise UserError('From Date And To Date Should be Different')

        if values.get('date_to', False):
            if self.date_from:
                if values['date_to'] < str(self.date_from):
                    raise UserError('To Date Should be Greater then the From Date')
                if values['date_to']==str(self.date_from):
                    raise UserError('From Date And To Date Should be Different')
        res = super(HREmployeeIncomeTax, self).write(values)
        return res

    def unlink(self):
        for rec in self:
            if not rec.state=="Draft":
                raise UserError("You Can Delete the Records that are in the Draft State")
            if rec.employee_tax_lines:
                rec.employee_tax_lines.unlink()
        return super(HREmployeeIncomeTax, self).unlink()

    @api.onchange('tax_id')
    def _onchange_tax_info(self):
        for rec in self:
            if rec.tax_id:
                rec.date_from = rec.tax_id.date_from
                rec.date_to = rec.tax_id.date_to
                rec.year = rec.tax_id.year
            else:
                rec.date_from = ''
                rec.date_to = ''
                rec.year = ''

    @api.depends('employee_id')
    def _compute_employee_info(self):
        for rec in self:
            if rec.employee_id:
                allowances = 0
                retirement_days_flag = False
                retirement_remaining_days_amt = 0
                retire_installment = 0

                rec.code = rec.employee_id.code and rec.employee_id.code or ''
                rec.employee_cnic = rec.employee_id.cnic and rec.employee_id.cnic or ''
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.designation_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False

                # Get Employee Contract (in Running State)
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', '=', 'open')
                                                              ], order='id desc', limit=1)
                if contract_id:
                    rec.contract_id = contract_id.id
                    rec.basic_wage = contract_id.wage
                    allowances += contract_id.adhoc_allowance_2016
                    allowances += contract_id.personal_pay_amount
                    if contract_id.allowance_ids:
                        for allow in contract_id.allowance_ids:
                            allowances += allow.amount if not allow.allowance_id.special_flag else 0

                    if not contract_id.date_end and rec.tax_id and not rec.employee_id.re_appointed and rec.employee_id.retirement_date and rec.employee_id.retirement_date < rec.tax_id.date_to:
                        retire_installment = (rec.employee_id.retirement_date.month - rec.date_from.month) + (12 * (rec.employee_id.retirement_date.year - rec.date_from.year))
                        date_end = rec.employee_id.retirement_date
                        month_days = (date_end + relativedelta(day=31)).day
                        retirement_days_flag = True
                        retirement_remaining_days_amt = round((contract_id.gross_salary / month_days) * date_end.day)

                    elif contract_id.date_end and rec.tax_id and contract_id.date_end < rec.tax_id.date_to:
                        retire_installment = (contract_id.date_end.month - rec.date_from.month) + (12 * (contract_id.date_end.year - rec.date_from.year))
                        date_end = contract_id.date_end
                        month_days = (date_end + relativedelta(day=31)).day
                        retirement_days_flag = True
                        retirement_remaining_days_amt = round((contract_id.gross_salary / month_days) * date_end.day)

                else:
                    rec.basic_wage = 0

                rec.allowances = allowances
                if not contract_id.first_contract_date==contract_id.date_start:
                    # rec.per_month_gross_pay = rec.basic_wage + allowances
                    # rec.annual_gross_pay = round(rec.per_month_gross_pay * rec.installment, 2)
                    if rec.employee_tax_lines:
                        rec.manual_gross = 0

                    if not rec.employee_tax_lines:
                        total_installment = rec.installment + rec.employee_id.manual_slips
                        rec.net_income = rec.employee_id.manual_gross
                        if total_installment > 0:
                            rec.per_month_gross_pay = round(rec.annual_gross_pay / total_installment, 2)
                        else:
                            total_installment = 1
                            rec.per_month_gross_pay = round(rec.annual_gross_pay / total_installment, 2)

                if contract_id.first_contract_date==contract_id.date_start and not rec.create_from_compute_sheet:
                    total_installment = rec.installment + rec.employee_id.manual_slips
                    month_gross = rec.basic_wage + allowances
                    if retirement_days_flag:
                        rec.annual_gross_pay = round((month_gross * retire_installment) + rec.employee_id.manual_gross + retirement_remaining_days_amt)
                    else:
                        rec.annual_gross_pay = round((month_gross * rec.installment) + rec.employee_id.manual_gross)

                    rec.manual_gross = rec.employee_id.manual_gross
                    rec.manual_tax = rec.employee_id.manual_tax
                    rec.manual_slips = rec.employee_id.manual_slips
                    rec.net_income = rec.employee_id.manual_gross
                    if total_installment > 0:
                        rec.per_month_gross_pay = round(rec.annual_gross_pay / total_installment, 2)
                    else:
                        total_installment = 1
                        rec.per_month_gross_pay = round(rec.annual_gross_pay / total_installment, 2)
            else:
                rec.code = ''
                rec.employee_cnic = ''
                rec.department_id = False
                rec.designation_id = False

    @api.depends('annual_gross_pay', 'installment', 'tax_id')
    def _calc_tax_amount(self):
        for rec in self:
            if rec.tax_id:
                tax_slab_id = rec.tax_id.lines.filtered(lambda line: line.start_limit <= rec.annual_gross_pay <= line.end_limit)
                if tax_slab_id:
                    rec.tax_slab_id = tax_slab_id.id
                    fixed_amount = tax_slab_id.fixed_amount
                    exceeded_amount = rec.annual_gross_pay - tax_slab_id.start_limit
                    percentage_tax_amount = round(exceeded_amount * (tax_slab_id.percentage / 100), 2)
                    rec.total_tax_amount = round(fixed_amount + percentage_tax_amount + rec.adjustment_amt)
                    rec.total_tax_amount2 = round(fixed_amount + percentage_tax_amount)

    @api.depends('total_tax_amount', 'rebate_amt', 'tax_id')
    def _compute_payable_tax(self, bb=False):
        for rec in self:
            if rec.total_tax_amount > 0:
                rec.payable_tax = round(rec.total_tax_amount - rec.rebate_amt - rec.manual_tax)
                if bb:
                    if rec.installment > 0:
                        rec.per_month_tax = round((rec.payable_tax - rec.total_deducted_amount) / rec.installment, 2)
                else:
                    if rec.employee_tax_lines and any([not line.amount==0 for line in rec.employee_tax_lines]):
                        last_line = rec.employee_tax_lines[(len(rec.employee_tax_lines) - 1)]
                        rec.per_month_tax = last_line.amount
                    else:
                        rec.per_month_tax = round(rec.payable_tax / rec.installment, 2)
            else:
                rec.payable_tax = 0
                rec.per_month_tax = 0

    @api.depends('total_deducted_amount', 'adjustment_amt', 'rebate_amt', 'tax_id')
    def _calc_remaining_amount(self):
        for rec in self:
            # rec.remaining_amount = rec.payable_tax - rec.total_deducted_amount
            rec.remaining_amount = round(rec.total_tax_amount + rec.total_deducted_amount - rec.rebate_amt)

    # @api.depends('employee_tax_lines.deducted_amount')
    # def _calc_deducted_amount(self):
    #     for rec in self:
    #         prev_amt = rec.total_deducted_amount
    #         for line in rec.employee_tax_lines:
    #             rec.total_deducted_amount += line.deducted_amount
    #         rec.total_deducted_amount = rec.total_deducted_amount - prev_amt

    # Calculate the No. of the Months for which Tax Lines to be Create
    @api.depends('date_from', 'date_to')
    def _compute_months(self):
        for rec in self:
            installment = 0
            flag = False
            if rec.employee_id:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', '=', 'open')
                                                              ], order='id desc', limit=1)

                if contract_id and contract_id.date_end and rec.tax_id and contract_id.date_end > rec.tax_id.date_to:
                    installment = (rec.tax_id.date_to.month - rec.date_from.month) + (12 * (rec.tax_id.date_to.year - rec.date_from.year)) + 1
                    flag = True

                if contract_id and contract_id.date_end and rec.tax_id and contract_id.date_end < rec.tax_id.date_to:
                    installment = (contract_id.date_end.month - rec.date_from.month) + (12 * (contract_id.date_end.year - rec.date_from.year)) + 1
                    flag = True

                if not contract_id.date_end and not rec.employee_id.re_appointed and rec.employee_id.retirement_date and rec.employee_id.retirement_date < rec.date_to:
                    # installment = (rec.employee_id.retirement_date.month - rec.date_from.month) + (12 * (rec.employee_id.retirement_date.year - rec.date_from.year)) + 1
                    installment = (rec.employee_id.retirement_date.month - rec.date_from.month) + (12 * (rec.employee_id.retirement_date.year - rec.date_from.year))
                    flag = True

                if not flag and rec.date_from and rec.date_to:
                    installment = (rec.date_to.month - rec.date_from.month) + (12 * (rec.date_to.year - rec.date_from.year)) + 1
            rec.installment = installment

    # Calculate the Rebate Amount, whenever the rebate_rate and Total Tax Amount is changed
    @api.depends('rebate_rate', 'total_tax_amount')
    def _compute_rebate_amt(self):
        rebate_rate = (int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.rebate_rate')) or '25')
        for rec in self:
            if rec.employee_id.rebateCateg=='teaching':
                rec.rebate_amt = round((int(rebate_rate) * 0.01) * rec.total_tax_amount)

    @api.depends('tax_adjustment_lines', 'tax_adjustment_lines.amount')
    def _compute_adjustment_amt(self):
        for rec in self:
            amt = 0
            for line in rec.tax_adjustment_lines:
                amt += line.amount
            rec.adjustment_amt = round(amt)

    @api.depends('annual_income_adjustment_lines', 'annual_income_adjustment_lines.amount')
    def _compute_annual_income_adjustment_amt(self):
        for rec in self:
            amt = 0
            for line in rec.annual_income_adjustment_lines:
                amt += line.amount
            rec.annual_income_adjustment_amt = round(amt)

    # Creates the No. of the Lines / Installment (According to Installment No.) Also Change the Status to Done State.
    def action_done(self, date_from=None):
        for rec in self:
            if date_from is None:
                date_from = rec.date_from
            if not rec.tax_id:
                raise UserError(_("Please Select Tax Slab."))
            if rec.remaining_amount > 0:
                for i in range(int(rec.installment)):
                    date = date_from + relativedelta(months=i)
                    line_values = {
                        'employee_id': rec.employee_id.id,
                        'date': date,
                        'month': date.strftime('%B-%Y'),
                        'employee_tax_id': rec.id,
                        'amount': round(rec.per_month_tax),
                        'state': 'Draft',
                    }
                    self.env['hr.employee.income.tax.line'].create(line_values)
            rec.state = 'Done'

    def action_turn_to_draft(self):
        for rec in self:
            if rec.employee_tax_lines:
                if any([not line.state=='Draft' for line in rec.employee_tax_lines]):
                    raise UserError(_('All Tax Line should be in Draft'))
            rec.state = 'Draft'

    @api.depends('total_tax_amount2', 'adjustment_amt', 'manual_tax', 'total_deducted_amount', 'rebate_amt')
    def _calc_remaining_tax(self):
        for rec in self:
            rec.remaining_tax_payable = round(rec.total_tax_amount2 + rec.adjustment_amt - rec.manual_tax - rec.total_deducted_amount - rec.rebate_amt)
            if rec.remaining_tax_payable < 0:
                rec.remaining_tax_payable = 0

    @api.depends('employee_tax_lines', 'employee_tax_lines.state', 'employee_tax_lines.slip_id')
    def _calc_total_deduction2(self):
        for rec in self:
            dd2 = 0
            if rec.employee_tax_lines:
                paid_lines = rec.employee_tax_lines.filtered(lambda a: a.deducted_amount > 0)
                for paid_line in paid_lines:
                    dd2 += paid_line.deducted_amount
            rec.total_deducted_amount2 = round(dd2)


class HREmployeeIncomeTaxLine(models.Model):
    _name = "hr.employee.income.tax.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Employee Income Tax Lines'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Employee', tracking=True)
    employee_tax_id = fields.Many2one('hr.employee.income.tax', 'Employee Tax Ref.', tracking=True, index=True, ondelete='cascade')
    date = fields.Date('Date')
    month = fields.Char('Month')
    amount = fields.Float('Amount')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Deducted', 'Deducted')
                              ], string='Status')
    reference = fields.Char('Reference')
    slip_id = fields.Many2one('hr.payslip', 'Payslip')
    deducted_amount = fields.Float('Deducted Amount')
    difference = fields.Float('Diff', compute='_calc_diff', store=True)

    @api.depends('deducted_amount')
    def _calc_diff(self):
        for rec in self:
            if rec.deducted_amount > 0:
                if rec.slip_id:
                    rec.employee_tax_id.total_deducted_amount = 0
                    for ln in rec.employee_tax_id.employee_tax_lines:
                        rec.employee_tax_id.total_deducted_amount += ln.deducted_amount
                    # rec.employee_tax_id.total_deducted_amount = rec.employee_tax_id.total_deducted_amount - rec.employee_tax_id.adjustment_amt
                else:
                    rec.difference = rec.amount - rec.deducted_amount
                    rec.employee_tax_id.total_deducted_amount += rec.deducted_amount
