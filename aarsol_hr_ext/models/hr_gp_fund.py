from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
import logging
import math
import re

_logger = logging.getLogger(__name__)
import pdb


class HrGPFundRule(models.Model):
    _name = 'hr.fund.rule'
    _description = 'Hr Fund Rule'

    fund_type = fields.Selection([('gp_fund', 'GP Fund'),
                                  ('benevolent_fund', 'Benevolent Fund')
                                  ], string='Fund Type', required=True)

    age_limit = fields.Integer('Age Limit')
    installment = fields.Integer('Max Installments')
    interest = fields.Integer('Interest In %')
    max_amount = fields.Integer('Max Amount of Total Balance', required=True)


class HrGPFund(models.Model):
    _name = 'hr.gp.fund'
    _description = 'Hr GP Fund'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    code = fields.Char('No')
    employee_id = fields.Many2one('hr.employee', string='Name')
    designation_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Designation')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Depertment')
    section_id = fields.Many2one('hr.section', related='employee_id.section_id', string='Section')
    gp_line_ids = fields.One2many('hr.gp.fund.line', 'gp_id', string='Gp Fund Details')
    profit = fields.Boolean('Profit', default=True)
    opening_balance = fields.Integer('Opening Balance')
    profit_amount = fields.Integer('Profit On average cumulative Balance')
    total_monthly_contribution = fields.Integer(compute='total_monthly_amount', string='Total Amount Contribution')
    total_balance = fields.Integer(compute='total_amount', string='Total Amount')

    # running_balance = fields.Integer(compute='total_running_amount',string='Running balance')

    @api.depends('total_monthly_contribution', 'profit_amount')
    def total_amount(self):
        self.total_balance = self.total_monthly_contribution + self.profit_amount

    @api.depends('gp_line_ids.monthly_contribution')
    def total_monthly_amount(self):
        total_contribution = 0
        for rec in self.gp_line_ids:
            total_contribution += rec.monthly_contribution

        self.total_monthly_contribution = total_contribution + self.opening_balance


class HrGPFundLine(models.Model):
    _name = 'hr.gp.fund.line'
    _description = 'Hr GP Fund Line'

    month = fields.Date('Month', required=True)
    monthly_contribution = fields.Integer('Monthly Regular Contribution')
    running_balance = fields.Integer(compute='total_running', string='Running Balance')
    gp_id = fields.Many2one('hr.gp.fund', string='GP Fund')
    is_profit = fields.Boolean('Profit Calculated', default=False)

    @api.depends('monthly_contribution')
    def total_running(self):

        amount = self[0].gp_id.opening_balance
        profit = self[0].gp_id.profit_amount
        for rec in self:
            amount += rec.monthly_contribution
            if rec.is_profit==False:
                rec.running_balance = amount + profit
            else:
                rec.running_balance = amount

# class hrGPFund(models.Model):
#     _name = 'hr.gp.fund.line'
#     _description = 'Hr GP Fund Line'
#
#     month=fields.Date('Month',required=True)
#     monthly_contribution= fields.Inteager('Monthly Regular Contribution',reqired=True )
#     gp_id = fields.Many2one('hr.gp.fund', string='GP Fund')
