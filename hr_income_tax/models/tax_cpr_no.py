# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import pdb

import logging

_logger = logging.getLogger(__name__)


class TaxCPRNO(models.Model):
    _name = "tax.cpr.no"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'CPR NO'

    name = fields.Char('CPR NO')
    sequence = fields.Integer('Sequence')
    year = fields.Selection([('2020', '2020'),
                             ('2021', '2021'),
                             ('2022', '2022'),
                             ('2023', '2023'),
                             ('2024', '2024'),
                             ('2025', '2025'),
                             ('2026', '2026'),
                             ('2027', '2027'),
                             ('2028', '2028'),
                             ('2029', '2029'),
                             ('2030', '2030'),
                             ('2031', '2031'),
                             ('2032', '2032'),
                             ('2033', '2033'),
                             ('2034', '2034'),
                             ('2035', '2035'),
                             ('2036', '2036'),
                             ('2037', '2037'),
                             ('2038', '2038'),
                             ('2039', '2039'),
                             ('2040', '2040'),
                             ('2041', '2041'),
                             ('2042', '2042'),
                             ('2043', '2043'),
                             ('2044', '2044'),
                             ('2045', '2045'),
                             ('2046', '2046'),
                             ('2047', '2047'),
                             ('2048', '2048'),
                             ('2049', '2049'),
                             ('2050', '2050')
                             ], string='Year', tracking=True, index=True)
    month = fields.Selection([('January', 'January'),
                              ('February', 'February'),
                              ('March', 'March'),
                              ('April', 'April'),
                              ('May', 'May'),
                              ('June', 'June'),
                              ('July', 'July'),
                              ('August', 'August'),
                              ('September', 'September'),
                              ('October', 'October'),
                              ('November', 'November'),
                              ('December', 'December')
                              ], string='Month', tracking=True, index=True)

    period_name = fields.Char('Period Name', compute='_compute_period_name', store=True)
    date = fields.Date('Date', default=fields.Date.today())
    state = fields.Selection([('Draft', 'Draft'),
                              ('Done', 'Done'),
                              ('Cancel', 'Cancel')
                              ], string='Status', default='Draft')
    description = fields.Char('Description')

    def unlink(self):
        for rec in self:
            if not rec.state=="Draft":
                raise UserError("You Can Delete the Records that are in the Draft State")
        return super(TaxCPRNO, self).unlink()

    @api.depends('year', 'month')
    def _compute_period_name(self):
        for rec in self:
            if rec.year and rec.month:
                rec.period_name = rec.month + "-" + rec.year

    def action_done(self):
        for rec in self:
            rec.state = 'Done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'Cancel'

    def action_copy_crp_no(self):
        for rec in self:
            if rec.period_name:
                tax_lines = self.env['hr.employee.income.tax.line'].search([('month', '=', rec.period_name),
                                                                            ('state', '=', 'Deducted')])
                if tax_lines:
                    for tax_line in tax_lines:
                        already_exist = self.env['hr.employee.tax.cpr.no'].search([('employee_id', '=', tax_line.employee_id.id),
                                                                                   ('month', '=', rec.period_name),
                                                                                   ('cpr_no', '=', rec.id)])
                        if not already_exist:
                            already_exist = self.env['hr.employee.tax.cpr.no'].search([('employee_id', '=', tax_line.employee_id.id),
                                                                                       ('month', '=', rec.period_name)])
                        if already_exist:
                            continue

                        if not already_exist:
                            cpr_no_values = {
                                'name': rec.period_name,
                                'employee_id': tax_line.employee_id and tax_line.employee_id.id or False,
                                'cpr_no': rec.id,
                                'month': rec.period_name,
                                'employee_tax_id': tax_line.employee_tax_id and tax_line.employee_tax_id.id or False,
                                'tax_line_id': tax_line.id,
                                'state': 'Done',
                                'date': rec.date,
                            }
                            new_rec = self.env['hr.employee.tax.cpr.no'].create(cpr_no_values)


class HREmployeeTaxCPRNO(models.Model):
    _name = "hr.employee.tax.cpr.no"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee CPR NO'

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    date = fields.Date('Date', default=fields.Date.today())
    cpr_no = fields.Many2one('tax.cpr.no', 'CPR No', tracking=True)
    month = fields.Char('Month', tracking=True)
    employee_tax_id = fields.Many2one('hr.employee.income.tax', 'Tax')
    tax_line_id = fields.Many2one('hr.employee.income.tax.line', 'Tax Line')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Done', 'Done'),
                              ('Cancel', 'Cancel')
                              ], string='Status', default='Draft')
