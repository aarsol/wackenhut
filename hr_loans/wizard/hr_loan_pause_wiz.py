import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HRLoanPauseWiz(models.TransientModel):
    _name = 'hr.loan.pause.wiz'
    _description = 'Loan Pause Wizard'

    @api.model
    def _get_loan_id(self):
        if self.env.context.get('active_model', False)=='hr.loan' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    loan_id = fields.Many2one('hr.loan', string='Loan Ref.', default=_get_loan_id)
    date = fields.Date('Date', default=fields.Date.today())
    reason = fields.Text('Reason')
    paid_installments = fields.Integer('Paid Installments', compute='get_paid_installments')
    remaining_installments = fields.Integer('Remaining Installments', compute='get_remaining_installments')
    pause_months = fields.Integer('Pause For Months')
    next_installment_start_date = fields.Date('Next Installment Start From')

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

    @api.constrains('pause_months')
    def pause_months_constrains(self):
        for rec in self:
            last_entry = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id)], order='id desc', limit=1)
            pause_last_date = last_entry.paid_date + relativedelta(months=rec.pause_months)
            if pause_last_date > rec.loan_id.employee_id.retirement_date:
                raise UserError(_("Installments are Going Beyond the Employee Retirement, it Should be Before Retirement Date.🌈"))

    def action_loan_pause(self):
        for rec in self:
            notes_flag = True
            remaining_installments = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                                      ('paid', '!=', True),
                                                                      ], order='id asc')
            for remaining_installment in remaining_installments:
                if notes_flag:
                    notes = "Loan Installments are Paused For " + str(rec.pause_months)
                    notes_flag = False
                else:
                    notes = ''
                remaining_installment.paid_date = remaining_installment.paid_date + relativedelta(months=rec.pause_months)
                remaining_installment.notes = notes
                if remaining_installment.salary_input_id:
                    remaining_installment.salary_input_id.date = remaining_installment.salary_input_id.date + relativedelta(months=rec.pause_months)
                if remaining_installment.interest_salary_input_id:
                    remaining_installment.interest_salary_input_id.date = remaining_installment.interest_salary_input_id.date + relativedelta(months=rec.pause_months)

            # Create Record in Change log
            change_log_values = {
                'date': fields.Date.today(),
                'notes': "Loan has been Paused or Skipped For Months " + str(rec.pause_months),
                'loan_id': rec.loan_id and rec.loan_id.id or False
            }
            change_log_rec = self.env['hr.loan.change.log'].create(change_log_values)
