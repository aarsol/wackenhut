# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import pdb

import logging

_logger = logging.getLogger(__name__)


class HREmployeeAnnualIncomeAdjustment(models.Model):
    _name = "hr.employee.annual.income.adjustment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Employee Annual Income Adjustments'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Employee', tracking=True)
    employee_code = fields.Char('Employee Code', related="employee_id.code", store=True)
    department_id = fields.Many2one('hr.department', 'Department', tracking=True)
    designation_id = fields.Many2one('hr.job', 'Designation', tracking=True)
    employee_tax_id = fields.Many2one('hr.employee.income.tax', 'Employee Tax Ref.', tracking=True)
    tax_id = fields.Many2one('hr.income.tax', 'Tax Ref.', tracking=True)
    date = fields.Date('Date', default=fields.Date.today())
    amount = fields.Float('Amount')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Done', 'Done')
                              ], string='Status', default='Draft')
    description = fields.Char('Description')

    @api.model
    def create(self, values):
        if values['amount']==0:
            raise UserError('Amount Should not be Zero.')
        res = super(HREmployeeAnnualIncomeAdjustment, self).create(values)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('hr.employee.annual.income.adjustment')
            return res

    def unlink(self):
        for rec in self:
            if not rec.state=="Draft":
                raise UserError("You Can Delete the Records that are in the Draft State")
        return super(HREmployeeAnnualIncomeAdjustment, self).unlink()

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.designation_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False

    def action_done(self):
        for rec in self:
            tax_id = False
            tax_slab_id = int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.current_tax_slab'))
            if tax_slab_id:
                tax_id = self.env['hr.income.tax'].search([('id', '=', tax_slab_id)])

            if tax_id and rec.date < tax_id.date_from:
                raise UserError(_('Entered Date %s is not Specified in  Current Slab %s.') % (rec.date.strftime("%d-%b-%Y"), tax_id.date_from.strftime('%d-%b-%Y')))

            if not tax_id:
                tax_id = self.env['hr.income.tax'].search([('date_from', '<=', rec.date),
                                                           ('date_to', '>=', rec.date)
                                                           ], order='id desc', limit=1)
            if tax_id:
                rec.tax_id = tax_id.id
                employee_tax_id = self.env['hr.employee.income.tax'].search([('employee_id', '=', rec.employee_id.id),
                                                                             ('tax_id', '=', tax_id.id)])
                if employee_tax_id:
                    rec.employee_tax_id = employee_tax_id.id
                    date = rec.date + relativedelta(day=1)
                    lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', employee_tax_id.id), ('date', '>=', date)])
                    if not lines:
                        # Added @ 11-10-2021 (sarfraz@aarsol.com)
                        updated_total_income = rec.amount + rec.employee_tax_id.annual_gross_pay
                        if rec.employee_tax_id.tax_slab_id and updated_total_income >= rec.employee_tax_id.tax_slab_id.end_limit:
                            rec.employee_tax_id.annual_gross_pay = rec.employee_tax_id.annual_gross_pay + rec.amount
                            annual_income = rec.employee_tax_id.annual_gross_pay
                            new_tax_slab_id = tax_id.lines.filtered(lambda ln: ln.start_limit <= annual_income <= ln.end_limit)
                            fixed_amount = new_tax_slab_id.fixed_amount
                            exceeded_amount = annual_income - new_tax_slab_id.start_limit
                            percentage_tax_amount = round(exceeded_amount * (new_tax_slab_id.percentage / 100), 2)
                            rec.employee_tax_id.total_tax_amount = round(fixed_amount + percentage_tax_amount + rec.employee_tax_id.adjustment_amt)
                            rec.employee_tax_id.total_tax_amount2 = round(fixed_amount + percentage_tax_amount)

                            installment = (rec.employee_tax_id.date_to.month - rec.date.month) + (12 * (rec.employee_tax_id.date_to.year - rec.date.year)) + 1
                            rec.employee_tax_id.installment = installment
                            per_month = round(rec.employee_tax_id.remaining_tax_payable / installment)
                            rec.employee_tax_id.action_done(date_from=rec.date)

                    if lines:
                        install_months = len(lines)
                        # Add the annual Income adj amount to annual income
                        rec.employee_tax_id.annual_gross_pay = rec.employee_tax_id.annual_gross_pay + rec.amount
                        annual_income = rec.employee_tax_id.annual_gross_pay

                        new_tax_slab_id = tax_id.lines.filtered(lambda ln: ln.start_limit <= annual_income <= ln.end_limit)
                        fixed_amount = new_tax_slab_id.fixed_amount
                        exceeded_amount = annual_income - new_tax_slab_id.start_limit
                        percentage_tax_amount = round(exceeded_amount * (new_tax_slab_id.percentage / 100), 2)
                        rec.employee_tax_id.total_tax_amount = round(fixed_amount + percentage_tax_amount + rec.employee_tax_id.adjustment_amt)
                        rec.employee_tax_id.total_tax_amount2 = round(fixed_amount + percentage_tax_amount)

                        per_month = round(rec.employee_tax_id.remaining_tax_payable / install_months)
                        for line in lines:
                            if per_month > 0:
                                line.amount = per_month
                            else:
                                line.amount = 0
                else:
                    raise UserError(_('No Tax Detail or Schedule is found for Employee %s', (rec.employee_id.name)))
                rec.state = 'Done'
            else:
                raise UserError(_('No Tax Slab is Found, Neither in Configuration nor from Date Search.'))
