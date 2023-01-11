from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import math
import numpy as np
import numpy_financial as npf
import pdb


class EmployeePayrollStatusUpdateWiz(models.TransientModel):
    _inherit = 'employee.payroll.status.update.wiz'

    def get_principal_amount(self, loan_id):
        principal_amount = 0
        if loan_id:
            entry_rec = self.env['hr.loan.line'].search([('loan_id', '=', loan_id.id),
                                                         ('paid', '!=', True)
                                                         ], order='id asc', limit=1)
            if entry_rec:
                principal_amount = entry_rec.balance_amount + entry_rec.principal_amount
        return principal_amount

    def action_update_payroll_status(self):
        for rec in self:
            result = super().action_update_payroll_status()

            # Loans Handling
            employee_loans = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id)])
            if employee_loans:
                if self.payroll_status=='stop':
                    employee_loans.write({'loan_stop': True})
                if self.payroll_status=='start':
                    stop_request_id = self.env['hr.employee.payroll.status'].search([('employee_id', '=', self.employee_id.id),
                                                                                     ('payroll_status', '=', 'stop'),
                                                                                     ], order='id desc', limit=1)
                    if not stop_request_id:
                        raise UserError(_('For this Employee its Salary Stop request is not found. \nFor Loan Reschedule its Stop request is necessary'))
                    for loan in employee_loans:
                        notes_flag = True
                        remaining_installments = False
                        last_paid_entry = self.env['hr.loan.line'].search([('loan_id', '=', loan.id),
                                                                           ('paid', '=', True)
                                                                           ], order='id desc', limit=1)
                        if last_paid_entry:
                            remaining_installments = self.env['hr.loan.line'].search([('loan_id', '=', loan.id),
                                                                                      ('paid', '!=', True),
                                                                                      ('id', '>', last_paid_entry.id)
                                                                                      ], order='id asc')
                        if not last_paid_entry:
                            remaining_installments = self.env['hr.loan.line'].search([('loan_id', '=', loan.id),
                                                                                      ('paid', '!=', True)
                                                                                      ], order='id asc')
                        if remaining_installments:
                            remaining_installments.write({'to_be': False})
                            pause_months = (((self.date.year - stop_request_id.date.year) * 12) + (self.date.month - stop_request_id.date.month) - 1)

                            for remaining_installment in remaining_installments:
                                if notes_flag:
                                    notes = "Loan Installments are Paused Because of Salary Stop For (" + str(pause_months) + ") Months"
                                    notes_flag = False
                                else:
                                    notes = ''
                                remaining_installment.paid_date = remaining_installment.paid_date + relativedelta(months=pause_months)
                                remaining_installment.notes = notes
                                if remaining_installment.salary_input_id:
                                    remaining_installment.salary_input_id.date = remaining_installment.salary_input_id.date + relativedelta(months=pause_months)

                                if remaining_installment.interest_salary_input_id:
                                    remaining_installment.interest_salary_input_id.date = remaining_installment.interest_salary_input_id.date + relativedelta(months=pause_months)

                            # Create Record in Change log
                            change_log_values = {
                                'date': fields.Date.today(),
                                'notes': "Loan has been Paused or Skipped Because of Salary Stop/Start For Months (" + str(pause_months) + ")",
                                'loan_id': loan.id or False
                            }
                            change_log_rec = self.env['hr.loan.change.log'].create(change_log_values)
                        loan.loan_stop = False
