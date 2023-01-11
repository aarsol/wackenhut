import logging
import pdb

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class HREmployeeBackDateArrears(models.Model):
    _name = 'hr.employee.backdate.arrears'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Employee Back Date Arrears'
    # This Class is used for Back Date Increments in Allowances and Back Date Deductions
    # To be Include in the Current Month slip, Here you specify  the Allowance or deduction and
    # Period for which to be calculate

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Employee', tracking=True, required=True)
    employee_code = fields.Char('Employee Code', compute='_compute_employee_info', store=True)
    date_from = fields.Date("Date From", tracking=True)
    date_to = fields.Date("Date To", tracking=True)
    slip_month = fields.Date('Slip Month')
    date = fields.Date('Entry Date', default=fields.Date.today())
    department_id = fields.Many2one('hr.department', 'Department', compute='_compute_employee_info', store=True)
    job_id = fields.Many2one('hr.job', 'Job', compute='_compute_employee_info', store=True)
    contract_id = fields.Many2one('hr.contract', 'Contract', tracking=True, compute='_compute_employee_info', store=True)
    ttype = fields.Selection([('allowance', 'Allowance'),
                              ('deduction', 'Deduction'),
                              ], default='allowance', string="Type")
    allowance_ids = fields.Many2many('hr.salary.allowances', 'emp_bba_allowances_rel', 'emp_bba_id', 'allowance_id', 'Allowances')
    deduction_ids = fields.Many2many('hr.salary.deductions', 'emp_bba_deductions_rel', 'emp_bba_id', 'deduction_id', 'Deductions')
    other_amount = fields.Float('Other Amount')
    amount = fields.Float('Calculated Amount', compute='_calc_amount', store=True)
    total_amount = fields.Float('Total Amount', compute='_compute_total', store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')
                              ], 'Status', readonly=True, default='draft', tracking=True)
    slip_id = fields.Many2one('hr.payslip', 'Payslip')
    emp_salary_input_id = fields.Many2one('hr.emp.salary.inputs', 'Salary Input')
    calculation_type = fields.Selection([('Existing', 'Existing'),
                                         ('New', 'New'),
                                         ], default='New', tracking=True, index=True)
    note = fields.Text('Note', tracking=True)
    skip_calculation = fields.Boolean('Skip Calculation', default=False)

    contract_nature = fields.Selection([('current', 'Current'),
                                        ('expired', 'Expired')
                                        ], default='current', string='Contract Nature', tracking=True)
    calc_expired_contract_amount = fields.Boolean('Calc Expired Contract', default=False)
    expired_contract_amount = fields.Float('Expired Contract Amt', compute='_calc_expired_contract_amt', store=True)
    add_subtract_nature = fields.Selection([('plus', '+'),
                                            ('minus', '-'),
                                            ], string='Add/Subtract', tracking=True)

    other_deduction_input_id = fields.Many2one('hr.salary.inputs', 'Other Deduction Inputs', tracking=True)
    basic_pay_percentage = fields.Float('Basic Percentage', default=0.0)
    basic_max_limit = fields.Float('Max Amount Limit', default=0.0)

    @api.model
    def create(self, values):
        result = super(HREmployeeBackDateArrears, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('hr.employee.backdate.arrears')
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise ValidationError(_('Only Draft State Entries can be deleted.'))
        return super().unlink()

    @api.depends('employee_id')
    def _compute_employee_info(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_code = rec.employee_id.code and rec.employee_id.code or ''
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.job_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', 'in', ('draft', 'open'))
                                                              ], order='id desc', limit=1)
                if contract_id:
                    rec.contract_id = contract_id.id

    @api.onchange('ttype')
    def onchange_ttype(self):
        for rec in self:
            if rec.ttype and rec.ttype=='allowance':
                if rec.deduction_ids:
                    rec.write({'deduction_ids': [(5,)]})
            if rec.ttype and rec.ttype=='deduction':
                rec.write({'allowance_ids': [(5,)]})

    @api.constrains('slip_month', 'date_from', 'date_to')
    def slip_month_constrains(self):
        for rec in self:
            if not rec.skip_calculation and rec.date_to and rec.slip_month:
                slip_start_date = rec.slip_month + relativedelta(day=1)
                slip_end_date = rec.slip_month + relativedelta(day=31)
                if rec.date_to > slip_start_date:
                    raise UserError(_('Date End should be Before Slip Month'))

    @api.constrains('date_from', 'date_to')
    def date_period_constrains(self):
        for rec in self:
            if not rec.skip_calculation:
                if rec.date_to and rec.date_from and rec.date_from > rec.date_to:
                    raise UserError(_('Date From should be Before Date End'))

    @api.depends('employee_id', 'ttype', 'allowance_ids', 'deduction_ids', 'date_from', 'date_to')
    def _calc_amount(self):
        for rec in self:
            amount = 0
            # First check that whether this Allowance or Deduction Exit in the Contract or not
            if not rec.skip_calculation:
                if rec.employee_id:
                    if rec.contract_id:
                        if rec.allowance_ids:
                            emp_allowance_ids = self.env['hr.emp.salary.allowances'].search([('employee_id', '=', rec.employee_id.id),
                                                                                             ('contract_id', '=', rec.contract_id.id),
                                                                                             ('allowance_id', 'in', rec.allowance_ids.ids),
                                                                                             ])
                            if emp_allowance_ids and rec.date_from and rec.date_to:
                                dt_start = rec.date_from
                                while dt_start < rec.date_to:
                                    month_first_date = dt_start + relativedelta(day=1)
                                    month_last_date = dt_start + relativedelta(day=31)
                                    if dt_start >= month_first_date and rec.date_to <= month_last_date:
                                        days = (rec.date_to - dt_start).days + 1
                                    elif dt_start >= month_first_date and rec.date_to >= month_last_date:
                                        days = (month_last_date - dt_start).days + 1

                                    if days > 0:
                                        month_days = dt_start + relativedelta(day=31)
                                        month_days = month_days.day

                                        if rec.calculation_type=='New':
                                            for emp_allowance_id in emp_allowance_ids:
                                                amount = amount + ((emp_allowance_id.amount / month_days) * days)

                                        if rec.calculation_type=='Existing':
                                            for emp_allowance_id in emp_allowance_ids:
                                                slip_line = self.env['hr.payslip.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                                                ('date_from', '>=', month_first_date),
                                                                                                ('date_to', '<=', month_last_date),
                                                                                                ('code', '=', emp_allowance_id.code),
                                                                                                ('slip_id.state', '!=', 'cancel')], order='id desc', limit=1)
                                                if slip_line:
                                                    diff_amt = emp_allowance_id.amount - (abs(slip_line.total))
                                                    if diff_amt > 0:
                                                        amount = amount + ((diff_amt / month_days) * days)
                                    dt_start += relativedelta(months=1, day=1)

                        if rec.deduction_ids:
                            emp_deduction_ids = self.env['hr.emp.salary.deductions'].search([('employee_id', '=', rec.employee_id.id),
                                                                                             ('contract_id', '=', rec.contract_id.id),
                                                                                             ('deduction_id', 'in', rec.deduction_ids.ids),
                                                                                             ])
                            if emp_deduction_ids and rec.date_from and rec.date_to:
                                dt_start = rec.date_from
                                while dt_start < rec.date_to:
                                    month_first_date = dt_start + relativedelta(day=1)
                                    month_last_date = dt_start + relativedelta(day=31)
                                    if dt_start >= month_first_date and rec.date_to <= month_last_date:
                                        days = (rec.date_to - dt_start).days + 1
                                    elif dt_start >= month_first_date and rec.date_to >= month_last_date:
                                        days = (month_last_date - dt_start).days + 1
                                    if days > 0:
                                        month_days = dt_start + relativedelta(day=31)
                                        month_days = month_days.day
                                        if rec.calculation_type=='New':
                                            for emp_deduction_id in emp_deduction_ids:
                                                amount = amount + ((emp_deduction_id.amount / month_days) * days)
                                        if rec.calculation_type=='Existing':
                                            for emp_deduction_id in emp_deduction_ids:
                                                slip_line = self.env['hr.payslip.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                                                ('date_from', '>=', month_first_date),
                                                                                                ('date_to', '<=', month_last_date),
                                                                                                ('code', '=', emp_deduction_id.code),
                                                                                                ('slip_id.state', '!=', 'cancel')], order='id desc', limit=1)
                                                if slip_line:
                                                    diff_amt = emp_deduction_id.amount - (abs(slip_line.total))
                                                    if diff_amt > 0:
                                                        amount = amount + ((diff_amt / month_days) * days)
                                    dt_start += relativedelta(months=1, day=1)
                        rec.amount = round(amount)
                    else:
                        raise UserError(_('Employee Contract not Found'))

    def calc_salary_head_amount(self, emp_deduction_id=False):
        amount = 0
        for rec in self:
            if not rec.skip_calculation:
                if rec.date_from and rec.date_to:
                    dt_start = rec.date_from
                    while dt_start < rec.date_to:
                        month_first_date = dt_start + relativedelta(day=1)
                        month_last_date = dt_start + relativedelta(day=31)
                        if dt_start >= month_first_date and rec.date_to <= month_last_date:
                            days = (rec.date_to - dt_start).days + 1
                        elif dt_start >= month_first_date and rec.date_to >= month_last_date:
                            days = (month_last_date - dt_start).days + 1
                        if days > 0:
                            month_days = dt_start + relativedelta(day=31)
                            month_days = month_days.day
                            if rec.calculation_type=='New':
                                amount = amount + ((emp_deduction_id.amount / month_days) * days)
                            if rec.calculation_type=='Existing':
                                slip_line = self.env['hr.payslip.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                                ('date_from', '>=', month_first_date),
                                                                                ('date_to', '<=', month_last_date),
                                                                                ('code', '=', emp_deduction_id.code),
                                                                                ('slip_id.state', '!=', 'cancel')], order='id desc', limit=1)
                                if slip_line:
                                    diff_amt = emp_deduction_id.amount - (abs(slip_line.total))
                                    if diff_amt > 0:
                                        amount = amount + ((diff_amt / month_days) * days)
                        dt_start += relativedelta(months=1, day=1)
                amount = round(amount)
            else:
                amount = round(rec.amount)
        return amount

    @api.depends('other_amount', 'amount')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = rec.amount + rec.other_amount

    def action_confirm(self):
        input_id = self.env['ir.config_parameter'].sudo().get_param('aarsol_hr_ext.arrears_input_rule')
        if not input_id:
            raise UserError('Please First Configure the Input Type for the Arrears')
        for rec in self:
            # Create Inputs Only For Allowances , Deductions Will be Handle in the Payslip
            if rec.ttype=='allowance':
                emp_salary_input_id = self.env['hr.emp.salary.inputs'].create({
                    'employee_id': rec.employee_id.id,
                    'name': rec.employee_id.name + "- Arrears",
                    'amount': rec.total_amount,
                    'state': 'confirm',
                    'input_id': input_id,
                    'date': rec.slip_month,
                })
                rec.emp_salary_input_id = emp_salary_input_id.id
                rec.state = 'confirm'
            else:
                rec.state = 'confirm'

    def action_turn_to_draft(self):
        for rec in self:
            if rec.state=='confirm':
                if rec.slip_id:
                    raise UserError(_('Can not Turn to Draft, Payslip is Linked with this Entry'))
                rec.state = 'draft'

    def action_recompute(self):
        for rec in self:
            if not rec.slip_id:
                if rec.emp_salary_input_id:
                    rec.emp_salary_input_id.amount = rec.total_amount
