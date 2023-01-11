from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fiscal_year_start = fields.Char(string='Start Date', config_parameter='aarsol_hr_ext.fiscal_year_start', default='2020-07-01')
    fiscal_year_end = fields.Char(string='Last Date', config_parameter='aarsol_hr_ext.fiscal_year_end', default='2021-06-30')

    retirement_period = fields.Char(string='Retirement Period (Years)', config_parameter='aarsol_hr_ext.retirement_period', default='60')

    loan_input_rule = fields.Many2one("hr.salary.inputs", config_parameter='aarsol_hr_ext.loan_input_rule', string="Loan Input Type")
    advance_input_rule = fields.Many2one("hr.salary.inputs", config_parameter='aarsol_hr_ext.advance_input_rule', string="Advance Input Type")
    arrears_input_rule = fields.Many2one("hr.salary.inputs", config_parameter='aarsol_hr_ext.arrears_input_rule', string="Arrears Input Type", help="Used in Back Date Arrears and broken Period Arrears")
    prev_deduction_input_rule = fields.Many2one("hr.salary.inputs", config_parameter='aarsol_hr_ext.prev_deduction_input_rule', string="Prev Deduction Input Type", help="Used Broken Period Prev. Deduction")

    attendance_policy = fields.Selection([('none', 'No Attendance'),
                                          ('daily', 'Daily Attendance'),
                                          ('monthly', 'Monthly Attendance'),
                                          ('overtime', 'Overtime'),
                                          ('bio_month', 'Bio Device with Monthly Counting')
                                          ], config_parameter='aarsol_hr_ext.attendance_policy', default='monthly', string='Attendance Policy')
    # contract_arrears_threshold_days = fields.Char(string='Contract Arrears Threshold Value', config_parameter='aarsol_hr_ext.contract_arrears_threshold_days', default='24')
