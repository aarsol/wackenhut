import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import math
import numpy as np
import numpy_financial as npf


class HRSupplementaryLoanWiz(models.TransientModel):
    _name = 'hr.supplementary.loan.wiz'
    _description = 'Additional Loan  Wizard'

    @api.model
    def _get_loan_id(self):
        if self.env.context.get('active_model', False)=='hr.loan' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    loan_id = fields.Many2one('hr.loan', string='Loan Ref.', default=_get_loan_id)
    employee_id = fields.Many2one('hr.employee', related='loan_id.employee_id')
    date = fields.Date('Date', default=fields.Date.today())
    amount = fields.Float('Amount', required=True)

    retirement_remaining_months = fields.Integer('Retirement Remaining Months', related='loan_id.retirement_remaining_months', store=True)
    retirement_date = fields.Date('Retirement Date', related='employee_id.retirement_date', store=True)

    paid_installments = fields.Integer('Paid Installments', compute='get_paid_installments')
    remaining_installments = fields.Integer('Remaining Installments', compute='get_remaining_installments')
    remaining_principal_amount = fields.Float('Remaining Principal Amount', compute='_compute_principal_amount')
    remaining_interest_amount = fields.Float('Remaining Interest Amount', compute='_compute_interest_amount')
    remaining_total_amount = fields.Float('Remaining Total Amount', compute='_compute_total_remaining_amount')

    new_installment_months = fields.Integer('New Installment Months', required=True)
    new_principal_amount = fields.Float('New Principal Amount', compute="_compute_new_principal_amount")
    new_interest_amount = fields.Float('New Interest Amount', compute='_compute_new_interest_amount')
    new_total_amount = fields.Float('Total Amount', compute='_compute_total_new_amount')

    def get_paid_installments(self):
        for rec in self:
            paid_installments = 0
            if rec.loan_id:
                paid_installments = self.env['hr.loan.line'].search_count([('loan_id', '=', rec.loan_id.id),
                                                                           ('paid', '=', True)])
            rec.paid_installments = paid_installments

    def _compute_retirement_rem_months(self):
        for rec in self:
            num_months = 0
            if rec.retirement_date:
                num_months = (rec.retirement_date.month - rec.date.month) + ((rec.retirement_date.year - rec.date.year) * 12)
            rec.retirement_remaining_months = num_months

    @api.constrains('retirement_remaining_months', 'new_installment_months')
    def reschedule_months_constrains(self):
        for rec in self:
            if rec.new_installment_months and rec.retirement_remaining_months:
                if rec.new_installment_months > rec.retirement_remaining_months:
                    raise UserError(_("Installments are Going Beyond the Employee Retirement, it Should be Before Retirement Date.🌈"))

    def get_remaining_installments(self):
        for rec in self:
            remaining_installments = 0
            if rec.loan_id:
                if rec.loan_id:
                    remaining_installments = self.env['hr.loan.line'].search_count([('loan_id', '=', rec.loan_id.id),
                                                                                    ('paid', '!=', True)])
                rec.remaining_installments = remaining_installments

    @api.constrains('amount')
    def additional_amount_constrains(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError(_("Additional Amount Should be Greater then Zero.🌈"))

    def _compute_principal_amount(self):
        for rec in self:
            entry_rec = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                         ('paid', '!=', True)], order='id asc', limit=1)
            if entry_rec:
                rec.remaining_principal_amount = entry_rec.balance_amount + entry_rec.principal_amount
            else:
                rec.remaining_principal_amount = 0

    def _compute_interest_amount(self):
        for rec in self:
            remaining_interest_amount = 0
            entry_recs = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                          ('paid', '!=', True)])
            if entry_recs:
                for entry_rec in entry_recs:
                    remaining_interest_amount += entry_rec.interest_amount
            rec.remaining_interest_amount = remaining_interest_amount

    def _compute_total_remaining_amount(self):
        for rec in self:
            rec.remaining_total_amount = rec.remaining_principal_amount + rec.remaining_interest_amount

    @api.depends('remaining_principal_amount', 'amount')
    def _compute_new_principal_amount(self):
        for rec in self:
            rec.new_principal_amount = rec.remaining_principal_amount + rec.amount

    @api.depends('new_principal_amount', 'new_installment_months')
    def _compute_new_interest_amount(self):
        for rec in self:
            if rec.new_installment_months > 0:
                interest_amt = 0
                counter = 1
                interest_rate = rec.loan_id.loan_id.interest_rate / 100
                principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
                interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
                for i in range(1, rec.new_installment_months + 1):
                    counter += 1
                    principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
                    interest_amt += round(-(npf.ipmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
                rec.new_interest_amount = interest_amt
            else:
                rec.new_interest_amount = rec.remaining_interest_amount

    @api.depends('new_principal_amount', 'new_interest_amount')
    def _compute_total_new_amount(self):
        for rec in self:
            rec.new_total_amount = rec.new_principal_amount + rec.new_interest_amount

    def create_supplementary_loan(self):
        for rec in self:
            if rec.loan_id and rec.loan_id.lsp_move_id:
                raise UserError(_('This Loan is already Paid, You cannot perform this action.'))
            if rec.loan_id.wf_move_id:
                raise UserError(_('This Loan is already Write Off, You cannot perform this Action'))
            if not rec.loan_id.state=='paid':
                raise UserError(_('This action can only be performed in Paid State'))
            vals = {
                'employee_id': rec.loan_id and rec.loan_id.employee_id.id or False,
                'loan_id': rec.loan_id and rec.loan_id.id or False,
                'date': rec.date,
                'amount': rec.amount,
                'state': 'done',
            }
            sup_loan_id = self.env['hr.supplementary.loan'].create(vals)
            move_id = rec.create_accounting_entry()
            sup_loan_id.move_id = move_id and move_id.id or False
            # reschedule the Loan
            additional_loan_id = rec.action_loan_reschedule()
            # Create Record in Change log
            change_log_values = {
                'date': fields.Date.today(),
                'notes': "Additional Loan has been Added.",
                'loan_id': rec.loan_id and rec.loan_id.id or False
            }
            change_log_rec = self.env['hr.loan.change.log'].create(change_log_values)

    def create_accounting_entry(self):
        for rec in self:
            move_pool = self.env['account.move']
            name = _('Mr. %s Additional Loan') % rec.loan_id.employee_id.name
            line_ids = []
            move_id = False
            move = {
                'narration': name,
                'date': rec.date,
                'journal_id': rec.loan_id.journal_id and rec.loan_id.journal_id.id or False,
            }

            amt = rec.amount
            partner_id = rec.loan_id.employee_id.address_home_id and rec.loan_id.employee_id.address_home_id.id or False
            if not partner_id:
                partner_id = rec.employee_id.partner_id and rec.employee_id.partner_id.id or False

            if rec.loan_id.debit_account_id:
                debit_line = (0, 0, {
                    'name': name,
                    'date': rec.date,
                    'partner_id': partner_id,
                    'account_id': rec.loan_id.debit_account_id and rec.loan_id.debit_account_id.id or False,
                    'journal_id': rec.loan_id.journal_id and rec.loan_id.journal_id.id or False,
                    'debit': amt > 0.0 and amt or 0.0,
                    'credit': amt < 0.0 and -amt or 0.0,
                })
                line_ids.append(debit_line)

            if rec.loan_id.credit_account_id:
                credit_line = (0, 0, {
                    'name': name,
                    'date': rec.date,
                    'partner_id': partner_id,
                    'account_id': rec.loan_id.credit_account_id and rec.loan_id.credit_account_id.id or False,
                    'journal_id': rec.loan_id.journal_id.id and rec.loan_id.journal_id.id or False,
                    'debit': amt < 0.0 and -amt or 0.0,
                    'credit': amt > 0.0 and amt or 0.0,
                })
                line_ids.append(credit_line)
            move.update({'line_ids': line_ids})
            move_id = move_pool.create(move)
        return move_id

    def action_loan_reschedule(self):
        for rec in self:
            date_start_str = ''
            last_paid_entry = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                               ('paid', '=', True)
                                                               ], order='id desc', limit=1)
            remaining_installments = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                                      ('paid', '!=', True),
                                                                      ('id', '>', last_paid_entry.id),
                                                                      ], order='id asc')
            # SET All Installment Line = False
            remaining_installments.write({'to_be': False})

            counter = 1
            interest_rate = rec.loan_id.loan_id.interest_rate / 100
            principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
            interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
            payment_amt = round(principal_amt + interest_amt)
            balance_amt = round(rec.new_principal_amount - principal_amt)

            note_flag = True
            for i in range(1, rec.new_installment_months + 1):
                if i < len(remaining_installments) + 1:
                    remaining_installment = remaining_installments[i - 1]
                    notes = "Loan Rescheduling Performed"
                    remaining_installment.write({
                        'principal_amount': principal_amt,
                        'interest_amount': interest_amt,
                        'paid_amount': payment_amt,
                        'balance_amount': balance_amt,
                        'notes': notes if note_flag else '',
                        'to_be': True,
                    })
                    note_flag = False
                    if remaining_installment.salary_input_id:
                        remaining_installment.salary_input_id.amount = principal_amt
                    if remaining_installment.interest_salary_input_id:
                        remaining_installment.interest_salary_input_id.amount = interest_amt
                    date_start_str = remaining_installment.paid_date

                # Create New Entry, if you want to expand the Installments
                if i > len(remaining_installments):
                    date_start_str = date_start_str + relativedelta(months=+1)
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
                    # Principal Amount Entry
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
                        if rec.loan_id.loan_id.interest_salary_rule_id:
                            interest_rule_input_id = self.env['hr.salary.inputs'].search([('salary_rule_id', '=', rec.loan_id.loan_id.interest_salary_rule_id.id)])
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
                principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
                interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, rec.new_installment_months, rec.new_principal_amount)))
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
                'notes': "Loan has been Rescheduled.",
                'loan_id': rec.loan_id and rec.loan_id.id or False
            }
            change_log_rec = self.env['hr.loan.change.log'].create(change_log_values)
