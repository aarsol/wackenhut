# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
import pdb
import logging

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        for payslip in self:
            prev_gross_amount = 0
            prev_gross_line = payslip.line_ids.filtered(lambda line: line.code=='GROSS')
            if prev_gross_line:
                prev_gross_amount = prev_gross_line.total
            super(HrPayslip, payslip).compute_sheet()
            payslip.match_income_tax_entry(prev_gross_amount)
        return True

    def match_income_tax_entry(self, prev_gross_amount):
        for rec in self:
            date_end = False
            old_manual_gross = 0
            old_manual_tax = 0
            old_manual_slips = 0
            retirement_days_flag = False
            retirement_remaining_days_amt = 0
            other_inputs = False
            other_inputs_amount = 0
            prev_slips_amount = 0

            income_tax_line = rec.line_ids.filtered(lambda ln: ln.code=='INCTX')
            gross_line = rec.line_ids.filtered(lambda ln: ln.code=='GROSS')
            net_line = rec.line_ids.filtered(lambda ln: ln.code=='NET')
            taxable_gross = int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.taxable_income'))
            current_tax_slab_id = int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.current_tax_slab'))
            current_tax_slab_rec = self.env['hr.income.tax'].search([('id', '=', current_tax_slab_id)])

            # @add 03-11-2021
            other_inputs = self.env['hr.emp.salary.inputs'].search([('slip_id', '=', rec.id),
                                                                    ('input_id.input_type', '=', 'alw')])
            if other_inputs:
                for other_input_id in other_inputs:
                    other_inputs_amount += other_input_id.amount

            # If Employee Contract End Date and Tax slab and Contract End Date Greater then Tax Slab Date To
            # For example ---- Contract End Date is 2025-01-31 and Tax Slab Date to is 2021-06-30a
            # Calculate Installment From Tax Slab Date To and Payslip From Date.
            if rec.contract_id.date_end and current_tax_slab_rec and rec.contract_id.date_end > current_tax_slab_rec.date_to:
                installment = ((current_tax_slab_rec.date_to.month - rec.date_from.month) + 1) + (12 * (current_tax_slab_rec.date_to.year - rec.date_from.year))
                date_end = rec.contract_id.date_end

            # add (15-06--2021 for retired employee (issue was tht system was going to create a new line))
            # if Employee Contract End Date and Tax Slab and Employee Retirement Date is also present and Employee Retirement Date Less than payslip Date To and Contract End Date less than Tax Slab Date To
            #  Calculate Installment from Contract Date End and payslip From Date.
            elif rec.contract_id.date_end and current_tax_slab_rec and rec.employee_id.retirement_date and rec.employee_id.retirement_date < rec.date_to and rec.contract_id.date_end < current_tax_slab_rec.date_to:
                installment = ((rec.contract_id.date_end.month - rec.date_from.month) + 1) + (12 * (rec.contract_id.date_end.year - rec.date_from.year))
                if rec.contract_id.date_end.month==rec.date_from.month and installment==0:
                    installment = 1
                date_end = rec.contract_id.date_end
                month_days = (date_end + relativedelta(day=31)).day
                retirement_remaining_days_amt = round((gross_line.total / month_days) * date_end.day)
                retirement_days_flag = True

            # If Contract End Date and Tax Slab and Contract End Date is less than Tax Slab Date To.
            # Calculate Installment from Contract End Date and Payslip From Date.
            elif rec.contract_id.date_end and current_tax_slab_rec and rec.contract_id.date_end < current_tax_slab_rec.date_to:
                installment = ((rec.contract_id.date_end.month - rec.date_from.month) + 1) + (12 * (rec.contract_id.date_end.year - rec.date_from.year))
                # Added @ 07-11-2021
                if rec.contract_id.date_end.month==rec.date_from.month and installment==0:
                    installment = 1
                date_end = rec.contract_id.date_end
                month_days = (date_end + relativedelta(day=31)).day
                retirement_remaining_days_amt = round((gross_line.total / month_days) * date_end.day)
                retirement_days_flag = True
                # End

            # if not Contract End Date and Retirement Date and not re_appointed and retirement Date is less than Tax Slab To Date.
            # Calculate Installment from Retirement Date  and Payslip From Date.
            elif not rec.contract_id.date_end and rec.employee_id.retirement_date and not rec.employee_id.re_appointed and rec.employee_id.retirement_date < current_tax_slab_rec.date_to:
                installment = (rec.employee_id.retirement_date.month - rec.date_from.month) + (12 * (rec.employee_id.retirement_date.year - rec.date_from.year))
                date_end = rec.employee_id.retirement_date
                month_days = (date_end + relativedelta(day=31)).day
                retirement_days_flag = True
                retirement_remaining_days_amt = round((gross_line.total / month_days) * date_end.day)

            # Calculate Installment From Tax Slab Date To and Payslip From Date
            else:
                installment = ((current_tax_slab_rec.date_to.month - rec.date_from.month) + 1) + (12 * (current_tax_slab_rec.date_to.year - rec.date_from.year))
                date_end = current_tax_slab_rec.date_to

            if retirement_days_flag and rec.contract_id.date_end:
                installment = installment - 1

            search_tax_line = self.env['hr.employee.income.tax.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                              ('date', '>=', rec.date_from),
                                                                              ('date', '<=', rec.date_to),
                                                                              ], order='id asc', limit=1)

            if search_tax_line:
                old_manual_gross = search_tax_line.employee_tax_id.manual_gross
                old_manual_tax = search_tax_line.employee_tax_id.manual_tax
                old_manual_slips = search_tax_line.employee_tax_id.manual_slips

            if search_tax_line and search_tax_line.slip_id:
                if retirement_days_flag:
                    annual_income = round((gross_line.total * installment) + search_tax_line.employee_tax_id.net_income + search_tax_line.employee_tax_id.annual_income_adjustment_amt - search_tax_line.employee_tax_id.previous_month_gross - (other_inputs_amount * (installment - 1)), 2)

                else:
                    annual_income = round((gross_line.total * installment) + search_tax_line.employee_tax_id.net_income + search_tax_line.employee_tax_id.annual_income_adjustment_amt - search_tax_line.employee_tax_id.previous_month_gross - (other_inputs_amount * (installment - 1)), 2)

            else:
                if retirement_days_flag:
                    annual_income = round((gross_line.total * installment) + search_tax_line.employee_tax_id.net_income + search_tax_line.employee_tax_id.annual_income_adjustment_amt - (other_inputs_amount * (installment - 1)), 2)

                else:
                    # Check if contract starts in between month
                    if rec.contract_id.date_start and rec.contract_id.new_date_start and not rec.contract_id.date_start==rec.contract_id.new_date_start:
                        months = (rec.contract_id.new_date_start.month - rec.contract_id.date_start.month)
                        if months==1 and search_tax_line.employee_tax_id.date_from==rec.contract_id.new_date_start:
                            glines = self.env['hr.payslip.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                         ('date_from', '=', rec.contract_id.date_start + relativedelta(day=1)),
                                                                         ('slip_id.state', '!=', 'cancel'),
                                                                         ('code', '=', 'GROSS')])
                            g_amt = 0
                            for gline in glines:
                                g_amt = g_amt + gline.total
                            annual_income = round((gross_line.total * installment) + search_tax_line.employee_tax_id.net_income + g_amt + search_tax_line.employee_tax_id.annual_income_adjustment_amt - (other_inputs_amount * (installment - 1)), 2)
                        else:
                            annual_income = round((gross_line.total * installment) + search_tax_line.employee_tax_id.net_income + search_tax_line.employee_tax_id.annual_income_adjustment_amt - (other_inputs_amount * (installment - 1)), 2)
                    else:
                        annual_income = round((gross_line.total * installment) + search_tax_line.employee_tax_id.net_income + search_tax_line.employee_tax_id.annual_income_adjustment_amt - (other_inputs_amount * (installment - 1)), 2)

            if retirement_days_flag:
                annual_income = annual_income + retirement_remaining_days_amt

            if not old_manual_gross==rec.employee_id.manual_gross:
                annual_income = annual_income + rec.employee_id.manual_gross - old_manual_gross
                search_tax_line.employee_tax_id.write({'manual_gross': rec.employee_id.manual_gross,
                                                       'manual_tax': rec.employee_id.manual_tax,
                                                       'manual_slips': rec.employee_id.manual_slips,
                                                       })
            # else:
            #     annual_income = annual_income + rec.employee_id.manual_gross

            new_tax_slab_id = current_tax_slab_rec.lines.filtered(lambda ln: ln.start_limit <= annual_income <= ln.end_limit)
            if search_tax_line:
                search_tax_line.employee_tax_id.annual_gross_pay = annual_income
                search_tax_line.employee_tax_id._compute_payable_tax()
                search_tax_line.employee_tax_id._calc_remaining_amount()
                search_tax_line.employee_tax_id._calc_remaining_tax()

                deducted_amount = 0
                # If Current Payslip Gross is not Equal with Previous Month Gross
                dffff = abs(gross_line.total - round(search_tax_line.employee_tax_id.previous_month_gross))
                if ((not gross_line.total==round(search_tax_line.employee_tax_id.previous_month_gross)) and dffff > 20) \
                        or (not old_manual_gross==rec.employee_id.manual_gross) or (not old_manual_tax==rec.employee_id.manual_tax):
                    net_line.amount = net_line.amount - income_tax_line.amount
                    previous_income_tax = income_tax_line.amount
                    income_tax_line.amount = 0
                    if new_tax_slab_id:
                        search_tax_line.employee_tax_id.annual_gross_pay = annual_income
                        if not new_tax_slab_id.id==search_tax_line.employee_tax_id.tax_slab_id.id:
                            search_tax_line.employee_tax_id.tax_slab_id = new_tax_slab_id.id

                        fixed_amount = new_tax_slab_id.fixed_amount
                        exceeded_amount = annual_income - new_tax_slab_id.start_limit
                        percentage_tax_amount = round(exceeded_amount * (new_tax_slab_id.percentage / 100), 2)
                        search_tax_line.employee_tax_id.total_tax_amount = round(fixed_amount + percentage_tax_amount + search_tax_line.employee_tax_id.adjustment_amt)
                        search_tax_line.employee_tax_id.total_tax_amount2 = round(fixed_amount + percentage_tax_amount)

                        total_lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', search_tax_line.employee_tax_id.id),
                                                                                      ('state', '=', 'Draft'),
                                                                                      ('date', '>=', rec.date_from)])

                        lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', search_tax_line.employee_tax_id.id),
                                                                                ('state', '=', 'Draft'),
                                                                                ('date', '>=', rec.date_from),
                                                                                ('date', '<=', date_end)])

                        del_lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', search_tax_line.employee_tax_id.id),
                                                                                    ('state', '=', 'Draft'),
                                                                                    ('date', '<', rec.date_from)])

                        if search_tax_line and search_tax_line.slip_id:
                            if not old_manual_tax==rec.employee_id.manual_tax:
                                remaining_tax_amount = search_tax_line.employee_tax_id.total_tax_amount - search_tax_line.employee_tax_id.total_deducted_amount - previous_income_tax - rec.employee_id.manual_tax
                                search_tax_line.employee_tax_id.manual_tax = rec.employee_id.manual_tax
                            else:
                                remaining_tax_amount = search_tax_line.employee_tax_id.total_tax_amount - search_tax_line.employee_tax_id.total_deducted_amount - previous_income_tax - search_tax_line.employee_tax_id.manual_tax
                        else:
                            remaining_tax_amount = search_tax_line.employee_tax_id.total_tax_amount - search_tax_line.employee_tax_id.total_deducted_amount - search_tax_line.employee_tax_id.manual_tax

                        if (not old_manual_gross==rec.employee_id.manual_gross) or (not old_manual_gross==rec.employee_id.manual_gross):
                            # search_tax_line.employee_tax_id.total_tax_amount = search_tax_line.employee_tax_id.total_tax_amount + rec.employee_id.manual_tax - old_manual_tax
                            remaining_tax_amount = remaining_tax_amount - rec.employee_id.manual_tax + old_manual_tax
                        # else:
                        #     remaining_tax_amount = remaining_tax_amount - rec.employee_id.manual_tax

                        lines2 = total_lines - lines
                        if lines and remaining_tax_amount >= 0:
                            if search_tax_line and search_tax_line.slip_id:
                                lines = lines + search_tax_line
                            month_nums = len(lines)
                            per_month = round(remaining_tax_amount / month_nums, 2)
                            deducted_amount = per_month
                            for line in lines:
                                line.amount = per_month

                        if lines and remaining_tax_amount < 0:
                            per_month = 0
                            deducted_amount = per_month
                            for line in lines:
                                line.amount = per_month

                        if lines2:
                            for line2 in lines2:
                                line2.amount = 0

                        if del_lines:
                            for del_line in del_lines:
                                del_line.unlink()

                    # update the Payslip line Amount
                    if income_tax_line:
                        old_income_tax_amt = income_tax_line.amount
                        income_tax_line.amount = -deducted_amount
                        net_line.amount = net_line.amount - deducted_amount + abs(old_income_tax_amt)
                    search_tax_line.deducted_amount = deducted_amount
                    search_tax_line.slip_id = rec.id
                    search_tax_line.state = 'Deducted'

                # if Current Month Payslip Gross and Previous Month Payslip Gross Equal
                else:
                    total_lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', search_tax_line.employee_tax_id.id),
                                                                                  ('state', '=', 'Draft'),
                                                                                  ('date', '>=', rec.date_from)])

                    lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', search_tax_line.employee_tax_id.id),
                                                                            ('state', '=', 'Draft'),
                                                                            ('date', '>=', rec.date_from),
                                                                            ('date', '<=', date_end)])

                    del_lines = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', search_tax_line.employee_tax_id.id),
                                                                                ('state', '=', 'Draft'),
                                                                                ('date', '<', rec.date_from)])

                    lines2 = total_lines - lines
                    remaining_tax_amount = 0
                    if prev_gross_amount==0:
                        remaining_tax_amount = search_tax_line.employee_tax_id.remaining_tax_payable
                    if prev_gross_amount > 0:
                        remaining_tax_amount = search_tax_line.employee_tax_id.remaining_tax_payable + search_tax_line.amount

                    if lines and remaining_tax_amount >= 0:
                        if search_tax_line and search_tax_line.slip_id:
                            lines = lines + search_tax_line
                        month_nums = len(lines)
                        per_month = round(remaining_tax_amount / month_nums, 2)
                        search_tax_line.employee_tax_id.per_month_tax = per_month
                        deducted_amount = per_month
                        for line in lines:
                            line.amount = per_month

                    if lines and remaining_tax_amount < 0:
                        per_month = 0
                        deducted_amount = per_month
                        for line in lines:
                            line.amount = per_month

                    if lines2:
                        for line2 in lines2:
                            line2.amount = 0

                    if del_lines:
                        for del_line in del_lines:
                            del_line.unlink()

                    # update the Payslip line Amount
                    if income_tax_line:
                        old_income_tax_amt = income_tax_line.amount
                        income_tax_line.amount = -deducted_amount
                        net_line.amount = net_line.amount - deducted_amount + abs(old_income_tax_amt)

                    search_tax_line.deducted_amount = abs(income_tax_line.total)
                    search_tax_line.slip_id = rec.id
                    search_tax_line.state = 'Deducted'

                if not old_manual_gross==rec.employee_id.manual_gross:
                    search_tax_line.employee_tax_id.net_income = search_tax_line.employee_tax_id.net_income + gross_line.total - prev_gross_amount + rec.employee_id.manual_gross - old_manual_gross
                else:
                    search_tax_line.employee_tax_id.net_income = search_tax_line.employee_tax_id.net_income + gross_line.total - prev_gross_amount
                search_tax_line.employee_tax_id.previous_month_gross = gross_line.total

            # If Schedule is not Generated But Gross is Taxable
            # if not search_tax_line: (05-06-2021)
            if not search_tax_line:
                prev_slip_lines = self.env['hr.payslip.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                      ('date_from', '>=', current_tax_slab_rec.date_from),
                                                                      ('date_to', '<=', current_tax_slab_rec.date_to),
                                                                      ('slip_id', '!=', rec.id),
                                                                      ('slip_id.state', '!=', 'cancel'),
                                                                      ('code', '=', 'GROSS')])

                if prev_slip_lines:
                    for prev_slip_line in prev_slip_lines:
                        prev_slips_amount += prev_slip_line.total
                    annual_income = annual_income + prev_slips_amount

                if annual_income > taxable_gross:
                    create_income_tax_schedule = (self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.ir.create_income_tax_schedule') or True)
                    if create_income_tax_schedule:
                        if current_tax_slab_rec:
                            # Create New Entry in the Employee Tax and Also Schedule Entries
                            employee_tax_values = {
                                'employee_id': rec.employee_id.id,
                                'tax_id': current_tax_slab_rec.id,
                                'date_from': rec.date_from,
                                'date_to': current_tax_slab_rec.date_to,
                                'year': current_tax_slab_rec.year,
                                'contract_id': rec.contract_id and rec.contract_id.id or False,
                            }
                            employee_tax_rec = self.env['hr.employee.income.tax'].sudo().create(employee_tax_values)

                            # employee_tax_rec._compute_employee_info()
                            employee_tax_rec.create_from_compute_sheet = True
                            employee_tax_rec.annual_gross_pay = annual_income
                            employee_tax_rec._calc_tax_amount()
                            employee_tax_rec._compute_payable_tax()
                            employee_tax_rec._calc_remaining_amount()
                            employee_tax_rec._calc_remaining_tax()
                            employee_tax_rec.installment = installment
                            employee_tax_rec.total_deducted_amount += rec.employee_id.manual_tax
                            employee_tax_rec.action_done()
                            sub_search_tax_line = self.env['hr.employee.income.tax.line'].search([('employee_id', '=', rec.employee_id.id),
                                                                                                  ('date', '>=', rec.date_from),
                                                                                                  ('date', '<=', rec.date_to)
                                                                                                  ], order='id asc', limit=1)

                            if sub_search_tax_line:
                                if not income_tax_line:
                                    income_tax_line = rec.create_new_income_tax_line(sub_search_tax_line.amount)
                                    if income_tax_line:
                                        income_tax_line.amount = 0
                                        income_tax_line.amount = -sub_search_tax_line.amount
                                net_line.amount = net_line.amount - sub_search_tax_line.amount
                                sub_search_tax_line.deducted_amount = sub_search_tax_line.amount
                                sub_search_tax_line.slip_id = rec.id
                                sub_search_tax_line.state = 'Deducted'
                            employee_tax_rec.previous_month_gross = gross_line.total
                            employee_tax_rec.net_income = gross_line.total + prev_slips_amount

    # This Method is required for the Tax Line Creation in the Payslip Line
    # Called from Above @match_income_tax_entry
    def create_new_income_tax_line(self, amount):
        salary_tax_line = False
        for rec in self:
            if rec.struct_id:
                salary_rule = self.env['hr.salary.rule'].search([('code', '=', 'INCTX'), ('struct_id', '=', rec.struct_id.id)])
            else:
                salary_rule = self.env['hr.salary.rule'].search([('code', '=', 'INCTX')])
            rate = 100.00
            qty = 1.00
            tax_values = {
                'sequence': salary_rule.sequence,
                'code': salary_rule.code,
                'name': salary_rule.name,
                'note': salary_rule.note,
                'salary_rule_id': salary_rule.id,
                'contract_id': rec.contract_id.id,
                'employee_id': rec.employee_id.id,
                'amount': amount,
                'quantity': qty,
                'rate': rate,
                'slip_id': rec.id,
            }
            salary_tax_line = self.env['hr.payslip.line'].sudo().create(tax_values)
        return salary_tax_line

    def unlink(self):
        for rec in self:
            # Delete Payslip Cron Entry
            payslip_cron = self.env['hr.payslip.cron'].search([('slip_id', '=', rec.id)])
            if payslip_cron:
                payslip_cron.write({'state': 'draft'})
                payslip_cron.sudo().unlink()

            # Delete Income Tax Lines
            gross_line = rec.line_ids.filtered(lambda ln: ln.code=='GROSS')
            income_tax_ids = self.env['hr.employee.income.tax.line'].search([('slip_id', '=', rec.id)])
            if income_tax_ids:
                for line in income_tax_ids:
                    line.employee_tax_id.total_deducted_amount = line.employee_tax_id.total_deducted_amount - line.deducted_amount
                    line.employee_tax_id.net_income -= gross_line.total
                income_tax_ids.write({'state': 'Draft', 'deducted_amount': 0})
        return super(HrPayslip, self).unlink()
