import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class GpFundProfit(models.TransientModel):
    _name = 'gp.fund.wize'
    _description = 'Gp Fund Profit Wizard'

    @api.model
    def _get_employee(self):

        if self.env.context.get('active_model', False)=='hr.gp.fund' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    employee_ids = fields.Many2many('hr.gp.fund', string='Employee',
        help="""Only selected Employee will be Processed.""", default=_get_employee)
    profit = fields.Float(string="Profit on average cumulative balance %", required=True)

    def calculate_profit(self):
        for emp in self.employee_ids.filtered(lambda l: l.profit==True):
            month_search = emp.gp_line_ids.filtered(lambda l: l.is_profit==False)
            if len(month_search)==12:
                monthly_contribution = 0
                for amu in month_search:
                    monthly_contribution += amu.running_balance
                    month_search.update({'is_profit': True})
                profit = (monthly_contribution / 12) * (self.profit / 100)
                emp.update({'profit_amount': profit})
