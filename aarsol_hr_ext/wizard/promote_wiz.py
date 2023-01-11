import pdb
from odoo import api, fields, models, _


class GpFundProfit(models.TransientModel):
    _name = 'hr.employee.promote'
    _description = 'Employee Promote Wizard'

    @api.model
    def _get_employee(self):

        if self.env.context.get('active_model', False)=='hr.employee' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    employee_ids = fields.Many2many('hr.employee', string='Employee', help="""Only selected Employee will be Processed.""", default=_get_employee)

    def calculate_profit(self):
        for emp in self.employee_ids:
            if emp.stage < 30:
                emp.stage += 1
