# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    current_tax_slab = fields.Many2one("hr.income.tax", config_parameter='hr_income_tax.current_tax_slab', string="Income Tax Slab")
    taxable_income = fields.Char(string='Taxable Income', config_parameter='hr_income_tax.taxable_income', default='600000')
    create_income_tax_schedule = fields.Boolean(string='Create Income Tax Schedule', config_parameter='hr_income_tax.create_income_tax_schedule', default=True)
    rebate_rate = fields.Char(string='Rebate Rate', config_parameter='hr_income_tax.rebate_rate', default='25')
