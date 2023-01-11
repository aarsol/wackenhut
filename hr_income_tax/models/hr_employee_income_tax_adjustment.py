# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import pdb

import logging

_logger = logging.getLogger(__name__)


class HREmployeeIncomeTaxAdjustment(models.Model):
    _name = "hr.employee.income.tax.adjustment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Employee Income Tax Adjustments'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Employee', tracking=True)
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
        res = super(HREmployeeIncomeTaxAdjustment, self).create(values)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('hr.employee.income.tax.adjustment')
            return res

    def unlink(self):
        for rec in self:
            if not rec.state=="Draft":
                raise UserError("You Can Delete the Records that are in the Draft State")
        return super(HREmployeeIncomeTaxAdjustment, self).unlink()

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
                    if lines:
                        month_nums = len(lines)
                        per_month = round(rec.amount / month_nums)
                        for line in lines:
                            amt = line.amount + per_month
                            if amt > 0:
                                line.amount = line.amount + per_month
                            else:
                                line.amount = 0
                    if not lines:
                        raise UserError(_('There Should be Tax Lines Defines on which this Adjustment Will affect.'))
                    if rec.amount < 0:
                        rec.employee_tax_id.total_deducted_amount = rec.employee_tax_id.total_deducted_amount - rec.amount
                        employee_tax_id.payable_tax = employee_tax_id.payable_tax + rec.amount
                        employee_tax_id.total_tax_amount = employee_tax_id.total_tax_amount + rec.amount

                    if rec.amount > 0:
                        employee_tax_id.payable_tax = employee_tax_id.payable_tax + rec.amount
                        employee_tax_id.total_tax_amount = employee_tax_id.total_tax_amount + rec.amount

                else:
                    raise UserError(_('No Tax Detail or Schedule is found for Employee %s', (rec.employee_id.name)))
                rec.state = 'Done'
            else:
                raise UserError(_('No Tax Slab is Found, Neither in Configuration nor from Date Search.'))
