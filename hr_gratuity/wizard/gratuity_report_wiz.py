import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class GratuityReportWiz(models.TransientModel):
    _name = 'gratuity.report.wiz'
    _description = 'Gratuity Report Wizard'

    @api.model
    def _get_employee(self):
        if self.env.context.get('active_model', False)=='hr.employee' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    @api.model
    def _get_joining_date(self):
        if self.env.context.get('active_model', False)=='hr.employee' and self.env.context.get('active_id', False):
            doj = ''
            employee_id = self.env['hr.employee'].search([('id', '=', self.env.context['active_id'])])
            if employee_id:
                doj = employee_id.joining_date
            return doj

    @api.model
    def _get_leaving_date(self):
        if self.env.context.get('active_model', False)=='hr.employee' and self.env.context.get('active_id', False):
            dol = ''
            employee_id = self.env['hr.employee'].search([('id', '=', self.env.context['active_id'])])
            if employee_id:
                dol = employee_id.retirement_date
            return dol

    employee_id = fields.Many2one('hr.employee', 'Employee', default=_get_employee)
    joining_date = fields.Date('Joining Date', default=_get_joining_date)
    retired_date = fields.Date('Retired On', default=_get_leaving_date)
    authority = fields.Char('Authority')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self:self.env.user.company_id.id)
    gratuity_type = fields.Many2one('hr.gratuity.config.type', 'Type')
    is_death_case = fields.Boolean('Is Death Case?', default=False)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'gratuity.report.wiz',
            'form': data
        }
        return self.env.ref('hr_gratuity.action_gratuity_report').with_context(landscape=True).report_action(self, data=datas, config=False)
