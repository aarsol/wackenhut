# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import pdb

import logging

_logger = logging.getLogger(__name__)


class HRIncomeTax(models.Model):
    _name = "hr.income.tax"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Income Tax'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    date_from = fields.Date('From Date', tracking=True)
    date_to = fields.Date('To Date', tracking=True)
    year = fields.Char('Year', tracking=True, compute='_compute_year', store=True)
    state = fields.Selection([('Draft', 'Draft'),
                              ('Done', 'Done')], string='Status', tracking=True, default='Draft', index=True)
    lines = fields.One2many('hr.income.tax.line', 'tax_id', 'Tax Slabs')
    remarks = fields.Text('Remarks')

    _sql_constraints = [('tax_slab_uniq', 'UNIQUE(date_from, date_to)', 'Duplication Not Allowed.')]

    @api.model
    def create(self, values):
        res = super(HRIncomeTax, self).create(values)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('hr.income.tax')
        return res

    def unlink(self):
        for rec in self:
            if not rec.state=="Draft":
                raise UserError("You Can Delete the Records that are in the Draft State")
            if rec.lines:
                rec.lines.unlink()
        return super(HRIncomeTax, self).unlink()

    @api.depends('date_from', 'date_to')
    def _compute_year(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                year = rec.date_from.strftime('%Y') + "-" + rec.date_to.strftime('%Y')
            else:
                year = ''
            rec.year = year

    def action_done(self):
        for rec in self:
            if rec.lines:
                rec.lines.write({'state': 'Done'})
            rec.state = 'Done'

    def action_turn_to_draft(self):
        for rec in self:
            if rec.lines:
                rec.lines.write({'state': 'Draft'})
            rec.state = 'Draft'


class HRIncomeTaxLine(models.Model):
    _name = "hr.income.tax.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Income Tax Lines'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    start_limit = fields.Float('Start Limit')
    end_limit = fields.Float('End Limit')
    taxable_amount = fields.Float('Taxable Amount', compute="_compute_taxable_amount", store=True)
    fixed_amount = fields.Float('Fixed Amount')
    percentage = fields.Float('Percentage(%)')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Done', 'Done')
                              ], string='Status', tracking=True, default='Draft', index=True)
    tax_id = fields.Many2one('hr.income.tax', 'Income Tax', tracking=True)
    date_from = fields.Date('From Date', related="tax_id.date_from", store=True, tracking=True)
    date_to = fields.Date('To Date', related="tax_id.date_to", store=True, tracking=True)
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        res = super(HRIncomeTaxLine, self).create(values)
        if not res.name:
            res.name = "Tax Slab " + res.tax_id.year + " (" + str(int(res.start_limit)) + " to " + str(int(res.end_limit)) + ")  Rs." + str(int(res.fixed_amount)) + "+" + str(res.percentage) + "% Over " + str(int(res.start_limit))
        return res

    def unlink(self):
        return super(HRIncomeTaxLine, self).unlink()

    @api.depends('start_limit', 'end_limit')
    def _compute_taxable_amount(self):
        for rec in self:
            if rec.start_limit and rec.end_limit > 0:
                rec.taxable_amount = rec.end_limit - rec.start_limit
            else:
                rec.taxable_amount = 0
