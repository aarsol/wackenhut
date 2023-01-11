# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import pdb


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    # This function is called from the Salary Rules to get the Tax Amount from the Tax Statement of the employee
    def get_tax_amount(self, payslip):
        for rec in self:
            tax_amt = 0
            if rec and payslip.date_from and payslip.date_to:
                tax_line = self.env['hr.employee.income.tax.line'].search([('employee_id', '=', rec.id),
                                                                           ('date', '>=', payslip.date_from),
                                                                           ('date', '<=', payslip.date_to),
                                                                           ], order='id desc', limit=1)
                if tax_line:
                    tax_amt = tax_line.amount
                else:
                    tax_amt = 0
        return tax_amt


class HRContract(models.Model):
    _inherit = 'hr.contract'

    def create_employee_tax_schedule(self, r_flag=False):
        for rec in self:
            installment = 0
            old_manual_gross = 0
            old_manual_tax = 0
            old_manual_slips = 0
            retirement_days_flag = False
            retirement_remaining_days_amt = 0

            current_tax_slab_id = int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.current_tax_slab'))
            current_tax_slab_rec = self.env['hr.income.tax'].search([('id', '=', current_tax_slab_id)])
            taxable_gross = int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.taxable_income'))
            create_income_tax_schedule = (self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.ir.create_income_tax_schedule') or True)
            tax_slab_exist = self.env['hr.employee.income.tax.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                             ('date', '>=', rec.date_start + relativedelta(day=1)),
                                                                             ('state', '=', 'Draft'),
                                                                             ('employee_tax_id.tax_id', '=', current_tax_slab_rec.id)
                                                                             ], order='id asc', limit=1)
            if tax_slab_exist:
                lines3 = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', tax_slab_exist.employee_tax_id.id),
                                                                         ('state', '=', 'Draft'),
                                                                         ('date', '<', rec.date_start)])
                # 22-06-2021(SARFRAZ due to Promotion Problem)
                # if lines3:
                #     for ln3 in lines3:
                #         ln3.unlink()

                date_end = False
                old_manual_gross = tax_slab_exist.employee_tax_id.manual_gross
                old_manual_tax = tax_slab_exist.employee_tax_id.manual_tax
                old_manual_slips = tax_slab_exist.employee_tax_id.manual_slips

                if rec.date_end and current_tax_slab_rec and rec.date_end > current_tax_slab_rec.date_to:
                    installment = (current_tax_slab_rec.date_to.month - tax_slab_exist.date.month) + (12 * (current_tax_slab_rec.date_to.year - tax_slab_exist.date.year)) + 1
                    date_end = rec.date_end

                elif rec.date_end and current_tax_slab_rec and rec.date_end < current_tax_slab_rec.date_to:
                    installment = (rec.date_end.month - tax_slab_exist.date.month) + (12 * (rec.date_end.year - tax_slab_exist.date.year)) + 1
                    date_end = rec.date_end

                elif not rec.date_end and not rec.employee_id.re_appointed and rec.employee_id.retirement_date and rec.employee_id.retirement_date < current_tax_slab_rec.date_to:
                    installment = (rec.employee_id.retirement_date.month - tax_slab_exist.date.month) + (12 * (rec.employee_id.retirement_date.year - tax_slab_exist.date.year))
                    date_end = rec.employee_id.retirement_date
                    month_days = (date_end + relativedelta(day=31)).day
                    retirement_days_flag = True
                    retirement_remaining_days_amt = round((rec.gross_salary / month_days) * date_end.day)
                else:
                    installment = (current_tax_slab_rec.date_to.month - tax_slab_exist.date.month) + (12 * (current_tax_slab_rec.date_to.year - tax_slab_exist.date.year)) + 1
                    date_end = current_tax_slab_rec.date_to

                total_gross = (rec.gross_salary * installment) + tax_slab_exist.employee_tax_id.net_income + retirement_remaining_days_amt
                if not old_manual_gross==rec.employee_id.manual_gross:
                    total_gross = total_gross + rec.employee_id.manual_gross - old_manual_gross
                    tax_slab_exist.employee_tax_id.write({'manual_gross': rec.employee_id.manual_gross,
                                                          'manual_tax': rec.employee_id.manual_tax,
                                                          'manual_slips': rec.employee_id.manual_slips, })

                if total_gross > taxable_gross:
                    if create_income_tax_schedule:
                        if current_tax_slab_rec:
                            # update the Basic Salary According to New Contract
                            tax_slab_exist.employee_tax_id.write({'basic_wage': rec.wage,
                                                                  'allowances': rec.allowances_amount,
                                                                  'per_month_gross_pay': rec.wage + rec.allowances_amount, })

                            new_tax_slab_id = current_tax_slab_rec.lines.filtered(lambda ln: ln.start_limit <= total_gross <= ln.end_limit)
                            if new_tax_slab_id:
                                tax_slab_exist.employee_tax_id.write({'tax_slab_id': new_tax_slab_id.id,
                                                                      'annual_gross_pay': total_gross,
                                                                      'contract_id': rec.id,
                                                                      })
                                fixed_amount = new_tax_slab_id.fixed_amount
                                exceeded_amount = tax_slab_exist.employee_tax_id.annual_gross_pay - new_tax_slab_id.start_limit
                                percentage_tax_amount = round(exceeded_amount * (new_tax_slab_id.percentage / 100))
                                tax_slab_exist.employee_tax_id.total_tax_amount = round(fixed_amount + percentage_tax_amount + tax_slab_exist.employee_tax_id.adjustment_amt)
                                tax_slab_exist.employee_tax_id.total_tax_amount2 = round(fixed_amount + percentage_tax_amount)

                                total_lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', tax_slab_exist.employee_tax_id.id),
                                                                                              ('state', '=', 'Draft'),
                                                                                              ('date', '>=', rec.date_start)])

                                lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', tax_slab_exist.employee_tax_id.id),
                                                                                        ('state', '=', 'Draft'),
                                                                                        ('date', '>=', rec.date_start),
                                                                                        ('date', '<=', date_end)])

                                if not r_flag:
                                    remaining_tax_amount = tax_slab_exist.employee_tax_id.total_tax_amount - tax_slab_exist.employee_tax_id.total_deducted_amount
                                if r_flag:
                                    remaining_tax_amount = tax_slab_exist.employee_tax_id.total_tax_amount - tax_slab_exist.employee_tax_id.total_deducted_amount - tax_slab_exist.employee_tax_id.manual_tax

                                if not old_manual_gross==rec.employee_id.manual_gross:
                                    remaining_tax_amount = remaining_tax_amount - rec.employee_id.manual_tax + old_manual_tax

                                if tax_slab_exist.employee_tax_id.adjustment_amt < 0:
                                    remaining_tax_amount = remaining_tax_amount - tax_slab_exist.employee_tax_id.adjustment_amt

                                lines2 = total_lines - lines
                                if lines and remaining_tax_amount >= 0:
                                    month_nums = len(lines)
                                    # per_month = round(tax_slab_exist.employee_tax_id.payable_tax / month_nums, 2)
                                    per_month = round(remaining_tax_amount / month_nums)
                                    for line in lines:
                                        line.amount = per_month

                                if lines and remaining_tax_amount < 0:
                                    for line in lines:
                                        line.amount = 0

                                if lines2:
                                    for line2 in lines2:
                                        line2.amount = 0

            # Create New Entry in the Employee Tax and Also Schedule Entries
            else:
                employee_tax_rec = False
                date_end = False

                if rec.date_end and current_tax_slab_rec and rec.date_end > current_tax_slab_rec.date_to:
                    installment = (current_tax_slab_rec.date_to.month - rec.new_date_start.month) + (12 * (current_tax_slab_rec.date_to.year - rec.new_date_start.year)) + 1

                elif rec.date_end and current_tax_slab_rec and rec.date_end < current_tax_slab_rec.date_to:
                    installment = (rec.date_end.month - rec.new_date_start.month) + (12 * (rec.date_end.year - rec.new_date_start.year)) + 1

                elif not rec.date_end and current_tax_slab_rec and not rec.employee_id.re_appointed and rec.employee_id.retirement_date and rec.employee_id.retirement_date < current_tax_slab_rec.date_to:
                    installment = (rec.employee_id.retirement_date.month - rec.new_date_start.month) + (12 * (rec.employee_id.retirement_date.year - rec.new_date_start.year))
                    date_end = rec.employee_id.retirement_date
                    month_days = (date_end + relativedelta(day=31)).day
                    retirement_days_flag = True
                    retirement_remaining_days_amt = round((rec.gross_salary / month_days) * date_end.day)

                else:
                    installment = (current_tax_slab_rec.date_to.month - rec.new_date_start.month) + (12 * (current_tax_slab_rec.date_to.year - rec.new_date_start.year)) + 1

                total_gross = (rec.gross_salary * installment) + retirement_remaining_days_amt
                if not tax_slab_exist:
                    if create_income_tax_schedule:
                        gross_lines = self.env['hr.payslip.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                          ('date_from', '>=', current_tax_slab_rec.date_from),
                                                                          ('slip_id.state', '!=', 'cancel'),
                                                                          ('code', '=', 'GROSS')])
                        gross_amt = 0
                        for gross_line in gross_lines:
                            gross_amt = gross_amt + gross_line.total

                        employee_tax_rec = self.env['hr.employee.income.tax'].search([('date_from', '<=', rec.date_start),
                                                                                      ('employee_id', '=', rec.employee_id.id),
                                                                                      ('tax_id', '=', current_tax_slab_rec.id),
                                                                                      ], order='id desc', limit=1)

                        total_gross = total_gross + rec.employee_id.manual_gross + gross_amt
                        # if employee_tax_rec:
                        #     total_gross = total_gross + gross_amt
                        # else:
                        #     total_gross = total_gross + rec.employee_id.manual_gross + gross_amt

                if total_gross > taxable_gross:
                    if create_income_tax_schedule:
                        employee_tax_rec = self.env['hr.employee.income.tax'].search([('date_from', '<=', rec.date_start),
                                                                                      ('employee_id', '=', rec.employee_id.id),
                                                                                      ('tax_id', '=', current_tax_slab_rec.id),
                                                                                      ], order='id desc', limit=1)
                        if employee_tax_rec:
                            employee_tax_rec.create_from_compute_sheet = True
                            employee_tax_rec.annual_gross_pay = total_gross
                            employee_tax_rec.installment = installment
                            employee_tax_rec._calc_tax_amount()
                            employee_tax_rec._compute_payable_tax(bb=True)
                            # employee_tax_rec.total_deducted_amount += rec.employee_id.manual_tax
                            employee_tax_rec.action_done(date_from=rec.new_date_start)
                            employee_tax_rec.previous_month_gross = rec.gross_salary
                            if employee_tax_rec.employee_id and employee_tax_rec.employee_id.rebateCateg=='teaching':
                                rebate_rate = (int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.rebate_rate')) or '25')
                                employee_tax_rec.rebate_rate = rebate_rate

                        if not employee_tax_rec:
                            employee_tax_values = {
                                'employee_id': rec.employee_id.id,
                                'tax_id': current_tax_slab_rec.id,
                                # 'date_from': rec.date_start,
                                'date_from': rec.new_date_start,
                                'date_to': current_tax_slab_rec.date_to,
                                'year': current_tax_slab_rec.year,
                                'contract_id': rec.id,
                                'manual_slips': rec.employee_id.manual_slips,
                                'manual_gross': rec.employee_id.manual_gross,
                                'manual_tax': rec.employee_id.manual_tax,
                                'create_from_compute_sheet': False,
                            }
                            employee_tax_rec = self.env['hr.employee.income.tax'].sudo().create(employee_tax_values)
                            employee_tax_rec.annual_gross_pay = total_gross

                            employee_tax_rec._compute_employee_info()
                            employee_tax_rec._calc_tax_amount()
                            employee_tax_rec._compute_payable_tax()
                            # employee_tax_rec.total_deducted_amount += rec.employee_id.manual_tax
                            # 17-07-2021
                            # employee_tax_rec.action_done(date_from=rec.date_start)
                            employee_tax_rec.action_done(date_from=rec.new_date_start)
                            employee_tax_rec.previous_month_gross = rec.gross_salary
                            if employee_tax_rec.employee_id and employee_tax_rec.employee_id.rebateCateg=='teaching':
                                rebate_rate = (int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.rebate_rate')) or '25')
                                employee_tax_rec.rebate_rate = rebate_rate
