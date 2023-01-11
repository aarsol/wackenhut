from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from dateutil import relativedelta
import logging
import re
import pdb

# from __future__ import division
_logger = logging.getLogger(__name__)


def parse_date(td):
    resYear = float(td.days) / 365.0
    resMonth = (resYear - int(resYear)) * 365.0 / 30.0
    resDays = int((resMonth - int(resMonth)) * 30)
    resYear = int(resYear)
    resMonth = int(resMonth)
    return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (
                resMonth and (str(resDays) + "D") or "")


class HrGPFundLoan(models.Model):
    _name = 'hr.gp.fund.loan'
    _description = 'Hr GP Fund Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Name',required=True)
    designation_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Designation')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Depertment')
    section_id = fields.Many2one('hr.section', related='employee_id.section_id', string='Section')
    birthday = fields.Date(related='employee_id.birthday', string='Birthday')
    age = fields.Integer(compute='_compute_age', string='Employee age ')
    total_balance = fields.Integer(compute='_calculate_total', string='Total Balance')
    gp_advance= fields.Integer('GP Fund Advance',required=True)

    @api.depends('birthday')
    def _compute_age(self):
        for rec in self:
            if rec.birthday:
                st = datetime.strptime(str(rec.birthday), "%Y-%m-%d")
                en = datetime.strptime(str(time.strftime(OE_DFORMAT)), "%Y-%m-%d")
                rec.age = float((en - st).days) / 365.25

    @api.depends('employee_id')
    def _calculate_total(self):
        search_gp = self.env['hr.gp.fund'].search([('employee_id', '=', self.employee_id.id)])
        if search_gp:
            self.total_balance = search_gp.total_balance
