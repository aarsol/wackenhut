from odoo import api, fields, models,tools

class GpFundStatement(models.TransientModel):
    _name = 'gp.fund.statement.wize'
    _description = 'Gp Fund Statement'

    employee_id = fields.Many2one('hr.employee',string='Employee', required=True)
    start_date = fields.Date(string='Date From', required=True)
    end_date = fields.Date(string='Date To', required=True)



    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'gp.fund.statement.wize',
            'form': data
        }
        return self.env.ref('aarsol_hr_ext.action_report_gp_statement').with_context(landscape=False).report_action(self,data=datas,config=False)
