import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil import relativedelta
from odoo.exceptions import ValidationError, UserError
import math
import numpy as np
import numpy_financial as npf


class HRLoanInterestRescheduleWiz(models.TransientModel):
    _name = 'hr.loan.interest.reschedule.wiz'
    _description = 'Loan Interest Reschedule Wizard'

    @api.model
    def _get_loan_id(self):
        if self.env.context.get('active_model', False)=='hr.loan' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    loan_id = fields.Many2one('hr.loan', string='Loan Ref.', default=_get_loan_id)
    employee_id = fields.Many2one('hr.employee', related='loan_id.employee_id')
    date = fields.Date('Reschedule Date', default=fields.Date.today())
    paid_installments = fields.Integer('Paid Installments', compute='get_paid_installments')
    remaining_installments = fields.Integer('Remaining Installments', compute='get_remaining_installments')
    reschedule_months = fields.Integer('Reschedule Months')
    remaining_months = fields.Integer('Remaining Months', compute='get_remaining_installments')
    retirement_remaining_months = fields.Integer('Retirement Remaining Months', related='loan_id.retirement_remaining_months', store=True)
    principal_amount = fields.Float('Principal Amount', compute='_compute_principal_amount')
    retirement_date = fields.Date('Retirement Date', related='employee_id.retirement_date', store=True)
    reason = fields.Text('Reason')
    next_installment_start_date = fields.Date('Reschedule Installment Start From')
    old_interest_rate = fields.Float('Old Interest Rate', compute='_computer_old_interest_rate')
    new_interest_rate = fields.Float('New Interest Rate')

    def get_paid_installments(self):
        for rec in self:
            paid_installments = 0
            if rec.loan_id:
                paid_installments = self.env['hr.loan.line'].search_count([('loan_id', '=', rec.loan_id.id),
                                                                           ('paid', '=', True)])
            rec.paid_installments = paid_installments

    def get_remaining_installments(self):
        for rec in self:
            remaining_installments = 0
            if rec.loan_id:
                if rec.loan_id:
                    remaining_installments = self.env['hr.loan.line'].search_count([('loan_id', '=', rec.loan_id.id),
                                                                                    ('paid', '!=', True)])
                rec.remaining_installments = remaining_installments
                rec.remaining_months = remaining_installments

    @api.constrains('retirement_remaining_months', 'reschedule_months')
    def reschedule_months_constrains(self):
        for rec in self:
            if rec.reschedule_months and rec.retirement_remaining_months:
                if rec.reschedule_months > rec.retirement_remaining_months:
                    raise UserError(_("Installments are Going Beyond the Employee Retirement, it Should be Before Retirement Date.🌈"))

    def _compute_retirement_rem_months(self):
        for rec in self:
            num_months = 0
            if rec.retirement_date:
                num_months = (rec.retirement_date.month - rec.date.month) + ((rec.retirement_date.year - rec.date.year) * 12)
            rec.retirement_remaining_months = num_months

    def _compute_principal_amount(self):
        for rec in self:
            entry_rec = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                         ('paid', '!=', True)], order='id asc', limit=1)
            if entry_rec:
                rec.principal_amount = entry_rec.balance_amount + entry_rec.principal_amount
            else:
                rec.principal_amount = 0

    def _computer_old_interest_rate(self):
        for rec in self:
            if rec.loan_id and rec.loan_id.loan_id:
                rec.old_interest_rate = rec.loan_id.loan_id.interest_rate

    def action_interest_reschedule(self):
        for rec in self:
            # pdb.set_trace()
            if rec.loan_id and rec.loan_id.lsp_move_id:
                raise UserError(_('This Loan is already Paid, You cannot perform this action.'))
            if rec.loan_id.wf_move_id:
                raise UserError(_('This Loan is already Write Off, You cannot perform this Action'))
            if not rec.loan_id.state=='paid':
                raise UserError(_('This action can only be performed in Paid State'))
            date_start_str = ''
            remaining_installments = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                                      ('paid', '!=', True),
                                                                      ('paid_date', '>=', rec.next_installment_start_date)
                                                                      ], order='id asc')
            # SET All Installment Line = False
            remaining_installments.write({'to_be': False})

            counter = 1
            if rec.new_interest_rate > 0:
                interest_rate = rec.new_interest_rate / 100
            else:
                interest_rate = rec.loan_id.loan_id.interest_rate / 100

            amount_per_time = rec.principal_amount / rec.reschedule_months

            principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, rec.reschedule_months, rec.principal_amount)))
            interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, rec.reschedule_months, rec.principal_amount)))
            payment_amt = round(principal_amt + interest_amt)
            balance_amt = round(rec.principal_amount - principal_amt)

            notes_flag = True
            for i in range(1, rec.reschedule_months + 1):
                if i < len(remaining_installments) + 1:
                    remaining_installment = remaining_installments[i - 1]
                    if notes_flag:
                        notes = "Interest Rescheduling Performed"
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

                # Create New Entry, if you want to expand the Installments
                if i > len(remaining_installments):
                    date_start_str = date_start_str + relativedelta.relativedelta(months=+1)
                    line_id = self.env['hr.loan.line'].create({
                        'paid_date': date_start_str,
                        'employee_id': rec.employee_id.id,
                        'loan_id': rec.loan_id.id,
                        'principal_amount': principal_amt,
                        'interest_amount': interest_amt,
                        'paid_amount': payment_amt,
                        'balance_amount': balance_amt,
                        'to_be': True,
                    })

                    # lines creation in hr_salary_inputs
                    code = 'LOAN'
                    rule_input_id = False
                    if rec.loan_id.loan_id.salary_rule_id:
                        rule_input_id = self.env['hr.salary.inputs'].search([('salary_rule_id', '=', rec.loan_id.loan_id.salary_rule_id.id)])
                    if not rule_input_id:
                        raise UserError('Please First Configure the Input Type for the Loans')

                    input_id = self.env['hr.emp.salary.inputs'].create({
                        'employee_id': rec.employee_id.id,
                        'name': code,
                        'amount': round(principal_amt),
                        'state': 'confirm',
                        'input_id': rule_input_id and rule_input_id.id or False,
                        'date': date_start_str,
                    })
                    line_id.salary_input_id = input_id and input_id.id or False

                    # Interest Amount Entry
                    if interest_amt > 0:
                        interest_rule_input_id = False
                        if self.loan_id.interest_salary_rule_id:
                            interest_rule_input_id = self.env['hr.salary.inputs'].search([('salary_rule_id', '=', self.loan_id.interest_salary_rule_id.id)])
                        if not interest_rule_input_id:
                            raise UserError('Please First Configure the Interest Input Type for the Loans')

                        code = 'LOAN Interest'
                        interest_input_id = self.env['hr.emp.salary.inputs'].create({
                            'employee_id': rec.employee_id.id,
                            'name': code,
                            'amount': round(interest_amt),
                            'state': 'confirm',
                            'input_id': interest_rule_input_id and interest_rule_input_id.id or False,
                            'date': date_start_str,
                        })
                        line_id.interest_salary_input_id = interest_input_id and interest_input_id.id or False

                counter += 1
                principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, rec.reschedule_months, rec.principal_amount)))
                interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, rec.reschedule_months, rec.principal_amount)))
                payment_amt = round(principal_amt + interest_amt)
                balance_amt = round(balance_amt - principal_amt)

            # If Some Extra Installments are found, Delete These
            unlink_entries = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                              ('paid', '!=', True),
                                                              ('to_be', '=', False)
                                                              ], order='id asc')

            if unlink_entries:
                salary_input_ids = unlink_entries.mapped('salary_input_id')
                interest_salary_input_ids = unlink_entries.mapped('interest_salary_input_id')
                if salary_input_ids:
                    if any([sal.slip_id for sal in salary_input_ids]):
                        raise UserError('Some Entries have Slip Reference.')
                    salary_input_ids.write({'state': 'draft'})
                    salary_input_ids.sudo().unlink()
                if interest_salary_input_ids:
                    if any([sal.slip_id for sal in interest_salary_input_ids]):
                        raise UserError('Some Entries have Slip Reference.')
                    interest_salary_input_ids.write({'state': 'draft'})
                    interest_salary_input_ids.sudo().unlink()
                unlink_entries.sudo().unlink()

            # Create Record in Change log
            change_log_values = {
                'date': fields.Date.today(),
                'notes': "Interest Rate has been Rescheduled.",
                'loan_id': rec.loan_id and rec.loan_id.id or False
            }
            change_log_rec = self.env['hr.loan.change.log'].create(change_log_values)

            to_be_change_entries = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                                    ('paid', '!=', True),
                                                                    ('to_be', '=', True)
                                                                    ], order='id asc')
            if to_be_change_entries:
                to_be_change_entries.write({'to_be': False})
