import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class GenerateEmployeeIncomeTaxWiz(models.TransientModel):
    _name = 'generate.employee.income.tax.wiz'
    _description = 'Employee Income Tax Generation Wizard'

    tax_id = fields.Many2one('hr.income.tax', 'Tax')
    type = fields.Selection([('All Employee', 'All Employee'),
                             ('Specific Employee', 'Specific Employee')
                             ], string='Type', default='All Employee')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    def generate_income_tax(self):
        for rec in self:
            employee_recs = False
            if rec.type=='All Employee':
                employee_recs = self.env['hr.employee'].search([('status', '=', 1)])
            else:
                employee_recs = rec.employee_id

            if employee_recs:
                for employee_rec in employee_recs:
                    already_exist = self.env['hr.employee.income.tax'].search([('employee_id', '=', employee_rec.id),
                                                                               ('tax_id', '=', rec.tax_id.id)])
                    if already_exist:
                        continue
                    else:
                        basic_wage = 0
                        allowances_amount = 0
                        per_month_gross_pay = 0
                        annual_gross_pay = 0
                        total_tax_amount = 0
                        per_month_tax = 0

                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_rec.id),
                                                                      ('state', '=', 'open')], order='id desc', limit=1)
                        if contract_id:
                            basic_wage = contract_id.wage
                        allowances = self.env['hr.emp.salary.allowances'].search([('employee_id', '=', employee_rec.id)])
                        if allowances:
                            for allow in allowances:
                                allowances_amount += allow.amount

                        per_month_gross_pay = basic_wage + allowances_amount
                        annual_gross_pay = round(per_month_gross_pay * 12, 2)

                        tax_slab_id = rec.tax_id.lines.filtered(lambda line: line.start_limit <= annual_gross_pay <= line.end_limit)
                        if tax_slab_id:
                            fixed_amount = tax_slab_id.fixed_amount
                            exceeded_amount = annual_gross_pay - tax_slab_id.start_limit
                            percentage_tax_amount = round(exceeded_amount * (tax_slab_id.percentage / 100), 2)
                            total_tax_amount = fixed_amount + percentage_tax_amount
                            if total_tax_amount > 0:
                                per_month_tax = round(total_tax_amount / 12, 2)

                            tax_entry_values = {
                                'employee_id': employee_rec.id,
                                'code': employee_rec.code and employee_rec.code or '',
                                'department_id': employee_rec.department_id and employee_rec.department_id.id or False,
                                'designation_id': employee_rec.job_id and employee_rec.job_id.id or False,
                                'employee_cnic': employee_rec.cnic and employee_rec.cnic or '',
                                'date_from': rec.tax_id.date_from,
                                'date_to': rec.tax_id.date_to,
                                'year': rec.tax_id.year,
                                'tax_id': rec.tax_id.id,
                                'tax_slab_id': tax_slab_id.id,
                                'basic_wage': basic_wage,
                                'allowances': allowances_amount,
                                'per_month_gross_pay': per_month_gross_pay,
                                'annual_gross_pay': annual_gross_pay,
                                'installment': 12,
                                'total_tax_amount': total_tax_amount,
                                'per_month_tax': per_month_tax,
                                'state': 'Draft',
                            }
                            tax_entry_rec = self.env['hr.employee.income.tax'].create(tax_entry_values)
                            tax_entry_rec.action_done()
