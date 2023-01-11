import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil import relativedelta
from odoo.exceptions import ValidationError, UserError
import math
import numpy as np
import numpy_financial as npf


class BulkHRLoanInterestRescheduleWiz(models.TransientModel):
    _name = 'bulk.hr.loan.interest.reschedule.wiz'
    _description = 'Bulk Loan Interest Reschedule Wizard'

    loan_id = fields.Many2one('hr.loans', string='Loan Category')
    date = fields.Date('Reschedule Date', default=fields.Date.today())
    next_installment_start_date = fields.Date('Reschedule Installment Start From')
    old_interest_rate = fields.Float('Old Interest Rate', compute='_computer_old_interest_rate')
    new_interest_rate = fields.Float('New Interest Rate')
    employee_loan_ids = fields.Many2many('hr.loan', 'bulk_loan_interest_reschedule_rel', 'wiz_id', 'loan_id', 'Employee Loans')

    @api.depends('loan_id')
    def _computer_old_interest_rate(self):
        for rec in self:
            if rec.loan_id:
                rec.old_interest_rate = rec.loan_id.interest_rate
            else:
                rec.old_interest_rate = 0

    @api.onchange('loan_id')
    def _compute_loan_detail(self):
        for rec in self:
            if rec.loan_id:
                if rec.employee_loan_ids:
                    rec.write({'employee_loan_ids': [(5,)]})
                employee_loan_ids = self.env['hr.loan'].search([('loan_id', '=', rec.loan_id.id),
                                                                ('balance_amount', '>', 0)])
                if employee_loan_ids:
                    rec.write({'employee_loan_ids': [[6, 0, employee_loan_ids.ids]]})

    def _compute_principal_amount(self, employee_loan_id):
        for rec in self:
            principal_amount = 0
            entry_rec = self.env['hr.loan.line'].search([('loan_id', '=', employee_loan_id.id),
                                                         ('paid', '!=', True),
                                                         ], order='id asc', limit=1)
            if entry_rec:
                principal_amount = entry_rec.balance_amount + entry_rec.principal_amount
        return principal_amount

    def action_interest_reschedule(self):
        for rec in self:
            if rec.employee_loan_ids:
                interest_rate = 0
                for employee_loan_id in rec.employee_loan_ids:
                    employee_principal_amount = rec._compute_principal_amount(employee_loan_id)
                    if employee_loan_id and employee_loan_id.lsp_move_id:
                        raise UserError(_('This Loan is already Paid, You cannot perform this action.'))
                    if employee_loan_id.wf_move_id:
                        raise UserError(_('This Loan is already Write Off, You cannot perform this Action'))
                    if not employee_loan_id.state=='paid':
                        raise UserError(_('This action can only be performed in Paid State'))
                    date_start_str = ''
                    remaining_installments = self.env['hr.loan.line'].search([('loan_id', '=', employee_loan_id.id),
                                                                              ('paid', '!=', True),
                                                                              ('paid_date', '>=', rec.next_installment_start_date)
                                                                              ], order='id asc')
                    # SET All Installment Line = False
                    remaining_installments.write({'to_be': False})

                    counter = 1
                    if rec.new_interest_rate > 0:
                        interest_rate = rec.new_interest_rate / 100

                    principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, len(remaining_installments), employee_principal_amount)))
                    interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, len(remaining_installments), employee_principal_amount)))
                    payment_amt = round(principal_amt + interest_amt)
                    balance_amt = round(employee_principal_amount - principal_amt)

                    notes_flag = True
                    for remaining_installment in remaining_installments:
                        if notes_flag:
                            notes = "Bulk Interest Rescheduling Performed"
                            notes_flag = False
                        else:
                            notes = ''
                        remaining_installment.write({
                            'principal_amount': principal_amt,
                            'interest_amount': interest_amt,
                            'paid_amount': payment_amt,
                            'balance_amount': balance_amt,
                            'notes': notes,
                            'to_be': True,
                        })
                        if remaining_installment.salary_input_id:
                            remaining_installment.salary_input_id.amount = principal_amt
                        if remaining_installment.interest_salary_input_id:
                            remaining_installment.interest_salary_input_id.amount = interest_amt
                        date_start_str = remaining_installment.paid_date

                        counter += 1
                        principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, len(remaining_installments), employee_principal_amount)))
                        interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, len(remaining_installments), employee_principal_amount)))
                        payment_amt = round(principal_amt + interest_amt)
                        balance_amt = round(balance_amt - principal_amt)

                    # Create Record in Change log
                    change_log_values = {
                        'date': fields.Date.today(),
                        'notes': "Bulk Interest Rate has been Rescheduled.",
                        'loan_id': employee_loan_id.id,
                    }
                    change_log_rec = self.env['hr.loan.change.log'].create(change_log_values)
                    to_be_change_entries = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                                            ('paid', '!=', True),
                                                                            ('to_be', '=', True)
                                                                            ], order='id asc')
                    if to_be_change_entries:
                        to_be_change_entries.write({'to_be': False})

                # Change Loan Category Interest Rate
                rec.loan_id.interest_rate = rec.new_interest_rate
                rec.loan_id.message_post(body="Interest Rate Changed from Bulk Interest Reschedule Process.")
