import pdb
from odoo import api, fields, models, _


class GeneratePayslipWiz(models.TransientModel):
    _name = 'generate.payslip.wiz'
    _description = 'Generate Payslip Wizard'

    record_limit = fields.Integer('Record Limit', default=100)

    def action_generate_payslips(self):
        for rec in self:
            payslip_cron = self.env['hr.payslip.cron'].generate_slips(nlimit=rec.record_limit)
