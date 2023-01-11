# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_overtime_amount_limit = fields.Boolean(string='Apply Overtime Amount Limit', config_parameter='aarsol_hr_attendance_ext.apply_overtime_amount_limit', default=False)
    overtime_amount_limit = fields.Char(string='Overtime Amount Limit', config_parameter='aarsol_hr_attendance_ext.overtime_amount_limit', default='3500')
    overtime_input_rule = fields.Many2one("hr.salary.inputs", config_parameter='aarsol_hr_attendance_ext.overtime_input_rule', string="Overtime Input Type")

    apply_ot_config_rate = fields.Boolean(string='Apply OT Config Rate', config_parameter='aarsol_hr_attendance_ext.apply_ot_config_rate', default=False)
    overtime_rate = fields.Char(string='Overtime Rate', config_parameter='aarsol_hr_attendance_ext.overtime_rate', default='50')
    week_days_overtime_rate = fields.Char(string='Week Days Overtime Rate', config_parameter='aarsol_hr_attendance_ext.week_days_overtime_rate', default='80')
