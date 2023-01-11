import time
from datetime import datetime

import numpy_financial as npf
from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
import pdb


class HRLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Business Loan"

    def _compute_quota(self):
        for rec in self:
            if rec.num_quotas > 0:
                rec.amount_quota = rec.amount / rec.num_quotas
            else:
                rec.amount_quota = 0

    @api.depends('net_amount', 'paid_amount', 'paid_quotas')
    def _compute_remaining(self):
        for rec in self:
            rec.remaining_debt = rec.net_amount - (rec.paid_amount + rec.paid_quotas)

    name = fields.Char("Name", tracking=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    employee_code = fields.Char('Employee Code', related='employee_id.code', store=True)

    retirement_date = fields.Date('Retirement Date', related='employee_id.retirement_date', store=True)
    retirement_remaining_months = fields.Integer('Retirement Remaining Months', compute='_compute_retirement_rem_months', store=True)

    loan_id = fields.Many2one('hr.loans', 'Loan Rule', required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    amount = fields.Float('Loan Amount', required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    amount_quota = fields.Float(compute='_compute_quota', string='Share Amount', store=False)
    num_quotas = fields.Integer('No. of Installments', required=True, readonly=True, states={'draft': [('readonly', False)]})

    date_start = fields.Date('Loan Start Date', readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    date_payment = fields.Date('Date of Payment', readonly=True, states={'draft': [('readonly', False)]}, tracking=True)

    paid_quotas = fields.Integer('Shares paid', compute="_compute_amount", store=True)
    paid_amount = fields.Float('Paid Amount', compute="_compute_amount", store=True)
    total_amount = fields.Float(string="Total Amount", compute='_compute_amount', store=True)
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_amount', store=True)

    loan_line_ids = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    remaining_debt = fields.Float(compute='_compute_remaining', string='Balance', store=True)
    active = fields.Boolean('Active', default=True)
    note = fields.Text('Note')
    state = fields.Selection([('draft', 'Draft'),
                              ('validate', 'Confirmed'),
                              ('paid', 'Paid')
                              ], string='State', default='draft', tracking=True, index=True)

    journal_id = fields.Many2one('account.journal', related='loan_id.journal_id', string="Loan Journal")
    debit_account_id = fields.Many2one('account.account', 'Debit Account', readonly=True)
    credit_account_id = fields.Many2one('account.account', 'Credit Account', readonly=True)
    code = fields.Char(related='loan_id.code', store=True, string="Code", tracking=True)
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True)

    interest_amount = fields.Float('Interest Amount', compute='_compute_interest', store=True)
    net_amount = fields.Float('Net Amount', compute='_compute_net_amount', store=True)

    payment_channel = fields.Selection([('bank', 'Bank'),
                                        ('cash', 'Cash')
                                        ], string='Payment Mode', default='bank', tracking=True, index=True)
    basic_pay = fields.Float('Basic Pay', compute='_compute_basic_pay', store=True, default=0)
    interest_received_amount = fields.Float('Interest Received', compute='_compute_interest_received', store=True)
    supplementary_loan_amount = fields.Float('Additional Loan', compute='_compute_additional_amount', store=True)

    is_eligible = fields.Boolean('Is Eligible', default=False)
    eligible_message = fields.Char('eligible Message')

    supplementary_loan_ids = fields.One2many('hr.supplementary.loan', 'loan_id', 'Supplementary Loans')
    change_log_ids = fields.One2many('hr.loan.change.log', 'loan_id', 'Change Logs')
    guarantor_ids = fields.One2many('hr.loan.guarantor', 'loan_id', 'Guarantors')

    wf_move_id = fields.Many2one('account.move', 'Write off Accounting Entry')
    lsp_move_id = fields.Many2one('account.move', 'Lump Sum Accounting Entry')
    accounts_required = fields.Boolean('Accounts Required', default=False)
    old_data = fields.Boolean('Old Data', default=False)

    date_order = fields.Date('Office Order Date', readonly=True, states={'draft': [('readonly', False)]}, default=lambda *a: time.strftime('%Y-%m-%d'), tracking=True)
    office_order_no = fields.Char('Office Order No.', tracking=True)
    remaining_installments = fields.Integer('Remaining Installments', compute='_compute_remaining_installments', store=True)
    loan_stop = fields.Boolean('Loan Stop', default=False, tracking=True)

    def _check_dates(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        for loan in self:
            if loan.date_start < current_date or loan.date_payment:
                return False
        return True

    @api.model
    def create(self, values):
        loans = self.env['hr.loans'].browse(values['loan_id'])
        employee = self.env['hr.employee'].browse(values['employee_id'])

        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('state', '=', 'open')], order='id desc', limit=1)
        if not contract_id:
            contract_id = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('state', '=', 'draft')], order='id desc', limit=1)
        if not contract_id:
            contract_id = self.env['hr.contract'].search([('employee_id', '=', employee.id)], order='id desc', limit=1)

        if not employee.contract_ids or not contract_id:
            raise UserError(_('This Employee have no Contract, Please Define its Contract First.'))

        if employee:
            if values['amount'] <= 0 or values['num_quotas'] <= 0:
                raise UserError('Amount of Loan and the number of Shares to pay should be Greater than Zero')

            if values['amount'] > loans.amount_max:
                raise UserError(_('Amount of Loan for (%s) is greater than Allowed amount for (%s)') % (employee.name, loans.name))

            if values['num_quotas'] > loans.shares_max:
                raise UserError(_('Number of Installments for (%s) is greater than Allowed Installments for (%s)') % (employee.name, loans.name))

            amount_quota = values['amount'] / values['num_quotas']
            if amount_quota > (contract_id.wage * (loans.amount_percentage / 100.0)):
                raise UserError(_('The requested Loan Amount for  (%s) Exceed the (%s)%% of his Basic Salary (%s). The Loan cannot be registered') % (employee.name, loans.amount_percentage, contract_id.wage))
            res = super(HRLoan, self).create(values)
            if not res.name:
                res.name = self.env['ir.sequence'].next_by_code('hr.loan')
        return res

    def write(self, values):
        if values.get('amount', False):
            if values['amount'] > self.loan_id.amount_max:
                raise UserError(_('Amount of Loan for (%s) is greater than Allowed amount for (%s)') % (self.employee_id.name, self.loan_id.name))

        if values.get('num_quotas', False):
            if values['num_quotas'] > self.loan_id.shares_max:
                raise UserError(_('Number of Installments for (%s) is greater than Allowed Installments for (%s)') % (self.employee_id.name, self.loan_id.name))

        if values.get('amount', False) and self.num_quotas > 0:
            contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                          ('state', '=', 'open')
                                                          ], order='id desc', limit=1)
            amount_quota = values['amount'] / self.num_quotas
            if amount_quota > (contract_id.wage * (self.loan_id.amount_percentage / 100.0)):
                raise UserError(_('The requested Loan Amount for  (%s) Exceed the (%s)%% of his Basic Salary (%s). The Loan cannot be registered') % (self.employee_id.name, self.loan_id.amount_percentage, contract_id.wage))

        res = super(HRLoan, self).write(values)
        return res

    def loan_confirm(self):
        if not self.is_eligible:
            raise UserError(_('This Employee is not Eligible for Loan'))
        self.write({'state': 'validate'})

    def loan_turn_to_draft(self):
        for rec in self:
            if rec.move_id:
                raise UserError(_('Turn To Draft Action cannot be performed, because accounting entries are linked.'))
            if any([ln.payroll_id for ln in rec.loan_line_ids]):
                raise UserError(_("This Action cannot be performed. Some Entries are Linked with payslips."))
            if not rec.move_id:
                rec.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state!='draft':
                raise ValidationError(_('You can only delete Entries that are in draft state .'))
            if rec.loan_line_ids:
                if any([ln.payroll_id for ln in rec.loan_line_ids]):
                    raise UserError(_("This Action cannot be performed. Some Entries are Linked with payslips."))

                salary_input_ids = rec.loan_line_ids.mapped('salary_input_id')
                interest_salary_input_ids = rec.loan_line_ids.mapped('interest_salary_input_id')
                # Unlink Salary Inputs
                if salary_input_ids:
                    salary_input_ids.write({'state': 'draft'})
                    salary_input_ids.sudo().unlink()
                # Unlink Interest Salary Inputs
                if interest_salary_input_ids:
                    interest_salary_input_ids.write({'state': 'draft'})
                    interest_salary_input_ids.sudo().unlink()
                rec.loan_line_ids.sudo().unlink()
        return super(HRLoan, self).unlink()

    @api.depends('loan_line_ids', 'loan_line_ids.paid', 'loan_line_ids.principal_amount', 'supplementary_loan_amount')
    def _compute_amount(self):
        for loan in self:
            paid_lines = loan.loan_line_ids.filtered(lambda l: l.paid)
            if paid_lines:
                total_paid_amount = 0
                total_interest_received = 0
                for paid_line in paid_lines:
                    total_paid_amount += paid_line.principal_amount
                    total_interest_received += paid_line.interest_amount

                balance_amount = loan.net_amount - (total_paid_amount + total_interest_received)
                loan.total_amount = loan.net_amount
                loan.balance_amount = balance_amount
                loan.paid_amount = total_paid_amount
                loan.paid_quotas = total_interest_received

    @api.depends('loan_id', 'amount', 'loan_line_ids', 'loan_line_ids.interest_amount')
    def _compute_interest(self):
        for rec in self:
            interest_amount = 0
            if rec.loan_line_ids:
                for line in rec.loan_line_ids:
                    interest_amount += line.interest_amount
            rec.interest_amount = interest_amount

    @api.depends('loan_id', 'interest_amount', 'amount', 'supplementary_loan_amount')
    def _compute_net_amount(self):
        for rec in self:
            rec.net_amount = rec.amount + rec.interest_amount + rec.supplementary_loan_amount

    @api.depends('employee_id')
    def _compute_basic_pay(self):
        for rec in self:
            if rec.employee_id:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', '=', 'open')], order='id desc', limit=1)
                if not contract_id:
                    contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                                  ('state', '=', 'draft')], order='id desc', limit=1)
                if contract_id:
                    rec.basic_pay = contract_id.wage
                else:
                    rec.basic_pay = 0
            else:
                rec.basic_pay = 0

    @api.onchange('loan_id')
    def onchange_loan_id(self):
        for rec in self:
            if rec.loan_id:
                if rec.loan_id.apply_on_remaining_service:
                    if rec.employee_id.joining_date:
                        start = fields.Date.today()
                        end = rec.employee_id.retirement_date
                        diff = relativedelta.relativedelta(end, start)
                        years = diff.years
                        months = diff.months
                        days = diff.days
                        quotas = months + (years * 12)
                        if quotas > rec.loan_id.shares_max:
                            rec.num_quotas = rec.loan_id.shares_max
                        else:
                            rec.num_quotas = months + (years * 12)
                    else:
                        rec.num_quotas = rec.loan_id.shares_max
                else:
                    rec.num_quotas = rec.loan_id.shares_max
            else:
                rec.num_quotas = 0

    def action_check_eligibility(self):
        for rec in self:
            if rec.old_data:
                rec.is_eligible = True

            if not rec.old_data:
                rec.is_eligible = False
                if not rec.loan_id.eligibility_ids:
                    raise UserError(_("There are no Eligibility Rules set for this Loan Rule .🤔"
                                      "\n Please Define the Eligibility Rules Then Try It."))

                if rec.amount > rec.loan_id.amount_max:
                    raise UserError(_("Loan Amount is Greater then the Allowed Amount.😅"))

                if rec.num_quotas > rec.loan_id.shares_max:
                    raise UserError(_("Loan Installments are Greater then the Allowed Installments.😁"))

                for eligibility_id in rec.loan_id.eligibility_ids:
                    if eligibility_id.domain:
                        if self.env['hr.employee'].search(safe_eval(eligibility_id.domain) + [('id', '=', rec.employee_id.id)]):
                            start = rec.employee_id.joining_date
                            end = fields.Date.today()
                            diff = relativedelta.relativedelta(end, start)
                            years = diff.years
                            months = diff.months
                            days = diff.days
                            total_service = months + (years * 12)
                            if total_service >= int(eligibility_id.period):
                                rec.is_eligible = True
                                break
                            else:
                                rec.is_eligible = False
                                rec.eligible_message = "This Employee is not eligible For Loan"
                        else:
                            rec.is_eligible = False
                            rec.eligible_message = "This Employee is not eligible For Loan"

    def loan_pay(self):
        # do accounting entries here
        move_pool = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')

        for loan in self:
            if loan.accounts_required:
                if not loan.is_eligible:
                    raise UserError(_('This Employee is not Eligible for Loan'))

                default_partner_id = loan.employee_id.address_home_id.id
                name = _('Loans To Mr. %s') % (loan.employee_id.name)
                move = {
                    'narration': name,
                    'date': timenow,
                    'journal_id': loan.loan_id.journal_id.id,
                }

                amt = loan.amount
                partner_id = default_partner_id
                debit_account_id = loan.debit_account_id.id
                credit_account_id = loan.credit_account_id.id

                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0

                # analytic_tags = self.env['account.analytic.tag']
                # analytic_tags += self.employee_id.analytic_tag_id
                # analytic_tags += self.employee_id.department_id.analytic_tag_id
                # analytic_tags += self.employee_id.branch_id.analytic_tag_id
                # analytic_tags += self.employee_id.city_id.analytic_tag_id
                # analytic_tag_ids = [(6, 0, analytic_tags.ids)]

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': loan.loan_id.name,
                        'date': timenow,
                        'partner_id': partner_id,
                        'account_id': debit_account_id,
                        'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
                        'debit': amt > 0.0 and amt or 0.0,
                        'credit': amt < 0.0 and -amt or 0.0,
                        # 'analytic_tag_ids': analytic_tag_ids,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id and not loan.payment_channel=='cash':
                    credit_line = (0, 0, {
                        'name': loan.loan_id.name,
                        'date': timenow,
                        'partner_id': partner_id,
                        'account_id': credit_account_id,
                        'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
                        'debit': amt < 0.0 and -amt or 0.0,
                        'credit': amt > 0.0 and amt or 0.0,
                        # 'analytic_tag_ids': analytic_tag_ids,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

                if credit_account_id and loan.payment_channel=='cash':
                    statement_rec = self.env['account.bank.statement'].search([('date', '=', loan.date_order), ('state', '=', 'open')])
                    if statement_rec:
                        line_values = ({
                            'statement_id': statement_rec.id,
                            'name': name,
                            'journal_id': 6,
                            'date': loan.date_order,
                            'account_id': debit_account_id,
                            'entry_date': timenow,
                            'amount': -amt,
                        })
                        statement_line = self.env['account.bank.statement.line'].create(line_values)

                        # Credit Entry
                        credit_line = (0, 0, {
                            'name': loan.loan_id.name,
                            'date': timenow,
                            'partner_id': partner_id,
                            'account_id': credit_account_id,
                            'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
                            'debit': amt < 0.0 and -amt or 0.0,
                            'credit': amt > 0.0 and amt or 0.0,
                            # 'analytic_tag_ids': analytic_tag_ids,
                        })
                        line_ids.append(credit_line)
                        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

                    else:
                        raise UserError(_('There is no CashBook entry Opened for this Date. May be Cashbook Validated.'))

                move.update({'line_ids': line_ids})
                move_id = move_pool.create(move)
                loan.write({'move_id': move_id.id, 'state': 'paid'})
                # move_id.post()
                loan.compute_loan_line()

            else:
                loan.state = 'paid'
                # move_id.post()
                loan.compute_loan_line()
        return True

    def compute_loan_line(self):
        loan_line = self.env['hr.loan.line']
        input_obj = self.env['hr.emp.salary.inputs']
        loan_line.search([('loan_id', '=', self.id)]).unlink()
        # rule_input_id = self.env['ir.config_parameter'].sudo().get_param('aarsol_hr_ext.loan_input_rule')

        for loan in self:
            date_start_str = loan.date_start
            counter = 1
            interest_rate = loan.loan_id.interest_rate / 100
            amount_per_time = loan.amount / loan.num_quotas

            principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, loan.num_quotas, loan.amount)))
            interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, loan.num_quotas, loan.amount)))
            payment_amt = round(principal_amt + interest_amt)
            balance_amt = round(loan.amount - principal_amt)

            for i in range(1, loan.num_quotas + 1):
                line_id = loan_line.create({
                    'paid_date': date_start_str,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id,
                    'principal_amount': principal_amt,
                    'interest_amount': interest_amt,
                    'paid_amount': payment_amt,
                    'balance_amount': balance_amt,
                })

                # lines creation in hr_salary_inputs
                # Principal Amount Entry
                if principal_amt > 0:
                    rule_input_id = False
                    if self.loan_id.salary_rule_id:
                        rule_input_id = self.env['hr.salary.inputs'].search([('salary_rule_id', '=', self.loan_id.salary_rule_id.id)])
                    if not rule_input_id:
                        raise UserError('Please First Configure the Input Type for the Loans')

                    code = 'LOAN'
                    input_id = input_obj.create({
                        'employee_id': loan.employee_id.id,
                        'name': code,
                        'amount': round(principal_amt),
                        'state': 'confirm',
                        'input_id': rule_input_id and rule_input_id.id or False,
                        'date': date_start_str,
                        # 'loan_line' : line_id.id,
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
                    interest_input_id = input_obj.create({
                        'employee_id': loan.employee_id.id,
                        'name': code,
                        'amount': round(interest_amt),
                        'state': 'confirm',
                        'input_id': interest_rule_input_id and interest_rule_input_id.id or False,
                        'date': date_start_str,
                        # 'loan_line' : line_id.id,
                    })
                    line_id.interest_salary_input_id = interest_input_id and interest_input_id.id or False

                counter += 1
                date_start_str = date_start_str + relativedelta.relativedelta(months=+1)

                principal_amt = round(-(npf.ppmt(interest_rate / 12, counter, loan.num_quotas, loan.amount)))
                interest_amt = round(-(npf.ipmt(interest_rate / 12, counter, loan.num_quotas, loan.amount)))
                payment_amt = round(principal_amt + interest_amt)
                balance_amt = round(balance_amt - principal_amt)
        return True

    @api.depends('loan_line_ids', 'loan_line_ids.paid', 'loan_line_ids.interest_amount')
    def _compute_interest_received(self):
        for rec in self:
            interest_received = 0
            if rec.loan_line_ids:
                for line in rec.loan_line_ids:
                    if line.paid:
                        interest_received += line.interest_amount
            rec.interest_received_amount = interest_received

    @api.depends('supplementary_loan_ids', 'supplementary_loan_ids.amount')
    def _compute_additional_amount(self):
        for rec in self:
            supplementary_amount = 0
            if rec.supplementary_loan_ids:
                for supplementary_line in rec.supplementary_loan_ids:
                    supplementary_amount += supplementary_line.amount
            rec.supplementary_loan_amount = supplementary_amount

    @api.depends('employee_id', 'employee_id.birthday')
    def _compute_retirement_rem_months(self):
        for rec in self:
            num_months = 0
            if rec.retirement_date and rec.date_start:
                num_months = (rec.retirement_date.month - rec.date_start.month) + ((rec.retirement_date.year - rec.date_start.year) * 12) + 1
            rec.retirement_remaining_months = num_months

    @api.constrains('retirement_remaining_months', 'num_quotas')
    def installment_months_constrains(self):
        for rec in self:
            if not rec.old_data:
                if rec.retirement_remaining_months > 0:
                    if rec.num_quotas > rec.retirement_remaining_months:
                        raise UserError(_('Installment Months Should be Less then Retirement Months'))

    @api.depends('loan_line_ids', 'loan_line_ids.paid')
    def _compute_remaining_installments(self):
        for rec in self:
            if rec.loan_line_ids:
                rec.remaining_installments = self.env['hr.loan.line'].search_count([('loan_id', '=', rec.id),
                                                                                    ('paid', '!=', True)])
            else:
                rec.remaining_installments = 0


class HRLoanLine(models.Model):
    _name = "hr.loan.line"
    _description = "HR Loan Request Line"

    paid_date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    paid_amount = fields.Float(string="Paid Amount", required=True)
    paid = fields.Boolean(string="Paid")
    notes = fields.Text(string="Notes")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", index=True, auto_join=True, ondelete='cascade')
    payroll_id = fields.Many2one('hr.payslip', string="Payslip Ref.")

    principal_amount = fields.Float('Principal Amount')
    interest_amount = fields.Float('Interest Amount')
    balance_amount = fields.Float('Balance Amount')

    salary_input_id = fields.Many2one('hr.emp.salary.inputs', 'Salary Input Ref.')
    interest_salary_input_id = fields.Many2one('hr.emp.salary.inputs', 'Interest Salary Input Ref.')
    to_be = fields.Boolean(string='To Be', default=False)
