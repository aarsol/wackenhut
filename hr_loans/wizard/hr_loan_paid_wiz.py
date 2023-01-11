import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HRLoanPaidWiz(models.TransientModel):
    _name = 'hr.loan.paid.wiz'
    _description = "Lump Sum Payment Wizard"

    @api.model
    def _get_loan_id(self):
        if self.env.context.get('active_model', False)=='hr.loan' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    loan_id = fields.Many2one('hr.loan', string='Loan Ref.', default=_get_loan_id)
    date = fields.Date('Date', default=fields.Date.today())
    paid_installments = fields.Integer('Paid Installments', compute='get_paid_installments')
    remaining_installments = fields.Integer('Remaining Installments', compute='get_remaining_installments')
    principal_amount = fields.Float('Principal Amount', compute='_compute_principal_amount')
    journal_id = fields.Many2one('account.journal', string="Loan Journal", required=True)
    debit_account_id = fields.Many2one('account.account', 'Debit Account', required=True)
    credit_account_id = fields.Many2one('account.account', 'Credit Account', required=True)
    show_message_text = fields.Boolean('Show Message Text', compute='_compute_show_message_text')
    reason = fields.Text('Reason')

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

    def _compute_principal_amount(self):
        for rec in self:
            entry_rec = self.env['hr.loan.line'].search([('loan_id', '=', rec.loan_id.id),
                                                         ('paid', '!=', True)], order='id asc', limit=1)
            if entry_rec:
                rec.principal_amount = entry_rec.balance_amount + entry_rec.principal_amount
            else:
                rec.principal_amount = 0

    def action_loan_paid(self):
        for rec in self:
            if rec.loan_id and rec.loan_id.lsp_move_id:
                raise UserError(_('This Loan is already Paid.'))
            if rec.loan_id.wf_move_id:
                raise UserError(_('This Loan is already Write Off, You cannot perform this Action'))
            if not rec.loan_id.state=='paid':
                raise UserError(_('This action can only be performed in Paid State'))

            move_pool = self.env['account.move']
            name = _('Loans Received From Mr. %s') % (rec.loan_id.employee_id.name)
            line_ids = []
            move = {
                'narration': name,
                'date': rec.date,
                'journal_id': rec.journal_id and rec.journal_id.id or False,
            }

            amt = rec.principal_amount
            partner_id = rec.loan_id.employee_id.address_home_id and rec.loan_id.employee_id.address_home_id.id or False
            if not partner_id:
                partner_id = rec.employee_id.partner_id and rec.employee_id.partner_id.id or False

            if rec.debit_account_id:
                debit_line = (0, 0, {
                    'name': name,
                    'date': rec.date,
                    'partner_id': partner_id,
                    'account_id': rec.debit_account_id and rec.debit_account_id.id or False,
                    'journal_id': rec.journal_id and rec.journal_id.id or False,
                    'debit': amt > 0.0 and amt or 0.0,
                    'credit': amt < 0.0 and -amt or 0.0,
                })
                line_ids.append(debit_line)

            if rec.credit_account_id:
                credit_line = (0, 0, {
                    'name': name,
                    'date': rec.date,
                    'partner_id': partner_id,
                    'account_id': rec.credit_account_id and rec.credit_account_id.id or False,
                    'journal_id': rec.journal_id.id and rec.journal_id.id,
                    'debit': amt < 0.0 and -amt or 0.0,
                    'credit': amt > 0.0 and amt or 0.0,
                })
                line_ids.append(credit_line)

            move.update({'line_ids': line_ids})
            move_id = move_pool.create(move)
            rec.loan_id.lsp_move_id = move_id and move_id.id or False

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
                'notes': "Loan has been Paid By Lump Sum Amount.",
                'loan_id': rec.loan_id and rec.loan_id.id or False
            }
            change_log_rec = self.env['hr.loan.change.log'].create(change_log_values)

    def _compute_show_message_text(self):
        for rec in self:
            if rec.loan_id and rec.loan_id.lsp_move_id:
                rec.show_message_text = True
            else:
                rec.show_message_text = False
