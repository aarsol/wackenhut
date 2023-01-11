from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date, datetime
import pdb

import logging

_logger = logging.getLogger(__name__)


class HRSalaryPercentageType(models.Model):
    _name = "hr.salary.percentage.type"
    _description = 'HR Salary Percentage Type'

    name = fields.Char('Name')
    code = fields.Char('Code')
    is_fixed = fields.Boolean('Is Fixed', default=False)


class HRSalaryRules(models.Model):
    _name = "hr.salary.rules"
    _description = 'HR Salary Rules'

    salary_structure_id = fields.Many2one('hr.payroll.structure', 'Salary Structure')  # General, Teaching
    account_id = fields.Many2one('account.account', 'Account')
    allowance_id = fields.Many2one('hr.salary.allowances', 'Allowance')
    deduction_id = fields.Many2one('hr.salary.deductions', 'Deduction')
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.allowance_id.code or res.deduction_id.code:
            res.create_salary_rule()
        return res

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if not rec.salary_rule_id and (res.allowance_id.code or res.deduction.code):
                rec.create_salary_rule()
        return res

    def unlink(self):
        for rec in self:
            if rec.salary_rule_id and rec.salary_rule_id.structure_ids:
                raise ValidationError(_('Salary Rule is linked with Payroll Structure'))
            rec.salary_rule_id.unlink()
        return super().unlink()

    def create_salary_rule(self):
        code = self.allowance_id.code or self.deduction_id.code
        apply_on = 'allowance_ids' if self.allowance_id else 'deduction_ids'
        data = {
            'name': self.allowance_id.name or self.deduction_id.name,
            'code': code,
            'sequence': 50 if self.allowance_id else 150,
            'quantity': 1,
            'category_id': 2 if self.allowance_id else 4,  # 2: allowance, 4: Deduction
            'active': True,
            'appears_on_payslip': True,
            # 'company_id': 1,
            'condition_select': 'python',
            'condition_python': "result = True if len(contract.%s.filtered(lambda l: l.code == '%s' and not l.expired== True)) > 0 else  False" % (apply_on, code,),
            'amount_select': 'code',
            'amount_python_compute': "result = contract.%s.filtered(lambda l: l.code == '%s').amount" % (apply_on, code,),
            'account_debit': self.account_id.id if self.allowance_id else False,
            'account_credit': self.account_id.id if self.deduction_id else False,
            'structure_ids': [(4, self.salary_structure_id.id, None)],  # General, Teaching
            'struct_id': self.salary_structure_id.id,
        }
        rule = self.env['hr.salary.rule'].create(data)
        self.salary_rule_id = rule.id


class HRSalaryPercentage(models.Model):
    _name = "hr.salary.percentage"
    _description = "HR Salary Percentage"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    domain = fields.Char('Domain Rule')  # hr.employee domain
    value = fields.Float('Value')
    min_value = fields.Float('Minimum Amount')
    max_value = fields.Float('Maximum Amount')

    allowance_id = fields.Many2one('hr.salary.allowances', 'Allowance')
    deduction_id = fields.Many2one('hr.salary.deductions', 'Deduction')
    note = fields.Html('Note')
    history_ids = fields.One2many('hr.salary.percentage.history', 'percentage_id', 'History')

    @api.model_create_multi
    def create(self, values):
        res = super().create(values)
        data = {
            'percentage_id': res.id,
            'allowance_id': res.allowance_id.id,
            'deduction_id': res.deduction_id.id,
            'date': datetime.now(),
            'domain': res.domain,
            'value': res.value,
            'min_value': res.min_value,
            'max_value': res.max_value,
        }
        self.env['hr.salary.percentage.history'].create(data)
        return res

    def write(self, vals):
        global data
        flag = True
        if vals.get('history_ids', False):
            flag = False

        if flag:
            prev_entry = self.env['hr.salary.percentage.history'].search([('percentage_id', '=', self.id)])
            if prev_entry:
                prev_entry.end_date = datetime.now()
            data = {
                'percentage_id': self.id,
                'allowance_id': self.allowance_id.id,
                'deduction_id': self.deduction_id.id,
                'date': datetime.now(),
                # 'end_date': datetime.now(),
                'domain': self.domain,
                'value': self.value,
                'min_value': self.min_value,
                'max_value': self.max_value,
            }
        res = super().write(vals)
        if flag:
            data['new_domain'] = self.domain
            data['new_value'] = self.value
            data['new_min_value'] = self.min_value
            data['new_max_value'] = self.max_value

            self.env['hr.salary.percentage.history'].create(data)
        return res


class HRSalaryPercentageHistory(models.Model):
    _name = "hr.salary.percentage.history"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "HR Salary Percentage History"
    _order = 'date desc'

    percentage_id = fields.Many2one('hr.salary.percentage', tracking=True)
    allowance_id = fields.Many2one('hr.salary.allowances', 'Allowance', tracking=True)
    deduction_id = fields.Many2one('hr.salary.deductions', 'Deduction', tracking=True)
    date = fields.Datetime('Start Date', tracking=True)
    end_date = fields.Datetime('End Date', tracking=True)
    domain = fields.Char('Prev. Domain Rule')  # hr.employee domain
    value = fields.Float('Prev. Value', tracking=True)
    min_value = fields.Float('Prev. Minimum Amount')
    max_value = fields.Float('Prev. Maximum Amount')

    new_domain = fields.Char('New Domain Rule')  # hr.employee domain
    new_value = fields.Float('New Value')
    new_min_value = fields.Float('New Minimum Amount')
    new_max_value = fields.Float('New Maximum Amount')


class HRSalaryAllowances(models.Model):
    _name = "hr.salary.allowances"
    _description = 'HR Salary Allowances'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    code = fields.Char('Code', tracking=True)

    percentage_type_id = fields.Many2one('hr.salary.percentage.type', 'Percentage Type')  # Freezed/IBP/RBP
    taxable = fields.Boolean('Taxable')
    percentage_ids = fields.One2many('hr.salary.percentage', 'allowance_id', 'ALW Calculations')
    rule_ids = fields.One2many('hr.salary.rules', 'allowance_id', 'Salary rules')
    lines = fields.One2many('hr.emp.salary.allowances', 'allowance_id', 'Employees/Contracts', domain=[('expired', '=', False)])
    active = fields.Boolean('Active', default=True, tracking=True)
    special_flag = fields.Boolean('Special', default=False, help="Use this field for Allowances not to add in Gross Allowances")
    date_start = fields.Date('Start Date', tracking=True)
    date_end = fields.Date('End Date', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    note = fields.Html('Note')

    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Allowance!"), ]

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            for rule in rec.rule_ids:
                if not rule.salary_rule_id and rec.code:
                    rule.create_salary_rule()
        return res

    def unlink(self):
        for rec in self:
            if rec.lines:
                raise ValidationError(_('Employees/structures are linked with Record'))
            if rec.rule_ids:
                raise ValidationError(_('Salary Rule is linked with Payroll Structure'))
        return super(HRSalaryAllowances, self).unlink()

    @api.constrains('date_start', 'date_end')
    def date_period_constrains(self):
        for rec in self:
            if rec.date_end and rec.date_start and rec.date_start > rec.date_end:
                raise ValidationError(_('Date Start should be Before Date End'))

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def show_warning_alert(self):
        warning = {}
        for rec in self:
            warning = {
                'title': _("Warning"),
                'message': "Alert"
            }
        return {'warning': warning}

    @api.onchange('active')
    def onchange_active_field(self):
        for rec in self:
            if not rec.active:
                emp_allowances = self.env['hr.emp.salary.allowances'].search([('allowance_id', '=', rec._origin.id)])
                if emp_allowances:
                    for emp_allowance in emp_allowances:
                        if emp_allowance.contract_id.state not in ('cancel', 'close'):
                            emp_allowance.write({'expired': True, 'expiry_date': fields.Date.today(), 'expiry_amount': emp_allowance.amount})


class HREmpSalaryAllowances(models.Model):
    _name = "hr.emp.salary.allowances"
    _description = 'HR Salary Allowances'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    contract_id = fields.Many2one('hr.contract', 'Contract', compute='_get_contract', store=True)
    employee_id = fields.Many2one('hr.employee', 'Employee')
    allowance_id = fields.Many2one('hr.salary.allowances', 'Allowance')
    code = fields.Char(related='allowance_id.code')
    payscale_id = fields.Many2one('hr.payscale', 'Payscale', compute='_get_contract', store=True, tracking=True)

    type = fields.Selection([('fixed', 'Fixed'),
                             ('formula', 'Formula')
                             ], 'Type', default='formula')
    amount_fixed = fields.Float('Fixed amt.', tracking=True)
    amount_formula = fields.Float(compute='calculate_amount', string='Formula amt', tracking=True)
    amount = fields.Float('Amount', tracking=True, compute='calculate_amount', inverse="_set_calculated_amount")

    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True, tracking=True)
    history_ids = fields.One2many('hr.benefit.history', 'allowance_id', 'History')
    expired = fields.Boolean('Expired', default=False)
    expiry_date = fields.Date('Expire Date')
    expiry_amount = fields.Float('Expiry Amount')
    salary_percentage_id = fields.Many2one('hr.salary.percentage', 'Salary Percentage')

    @api.depends('employee_id', 'allowance_id')
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, (rec.employee_id.name or '') + '/' + (rec.allowance_id.name or '')))
        return result

    @api.depends('employee_id')
    def _get_contract(self):
        for rec in self:
            if rec.employee_id:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], order='id desc', limit=1)
                rec.payscale_id = rec.employee_id.payscale_id and rec.employee_id.payscale_id.id or False
                # rec.contract_id = rec.employee_id.contract_ids and rec.employee_id.contract_ids[0].id or False
                rec.contract_id = contract_id and contract_id.id or False

    def _amount_formula(self):
        amount_formula = 0
        lines = []
        if self.salary_percentage_id:
            lines = self.salary_percentage_id
        for line in lines:
            # if not line.domain or self.env['hr.employee'].search(safe_eval(line.domain) + [('id', '=', self.employee_id.id)]):
            if line.allowance_id.percentage_type_id.code=='IBP':
                amount_formula = self.contract_id.basic_pay_initial * (line.value / 100)
                if line.min_value > 0:
                    amount_formula = max(line.min_value, amount_formula)
                if line.max_value > 0:
                    amount_formula = min(line.max_value, amount_formula)

            elif line.allowance_id.percentage_type_id.code=='RBP':
                amount_formula = (self.contract_id.personal_pay_amount + self.contract_id.basic_pay) * (line.value / 100)
                if line.min_value > 0:
                    amount_formula = max(line.min_value, amount_formula)
                if line.max_value > 0:
                    amount_formula = min(line.max_value, amount_formula)

            elif line.allowance_id.percentage_type_id.code=='Fixed':
                amount_formula = line.value
            break
        amount_formula = round(amount_formula, 0)
        return amount_formula

    def calculate_amount(self):
        for rec in self:
            rec.amount_formula = rec._amount_formula()
            if rec.type=='fixed':
                rec.amount = rec.amount_fixed
                rec.amount_formula = 0
            else:
                rec.amount = rec.amount_formula
                rec.amount_fixed = 0

    def _calculate_amount(self):
        if self.type=='fixed':
            return self.amount_fixed
        else:
            return self._amount_formula()

    # def _set_calculated_amount(self):
    #     pass

    def write(self, vals):
        data = {
            'employee_id': self.employee_id.id,
            'allowance_id': self.id,
            'deduction_id': False,
            'date': datetime.now(),
            'type': self.type,
            'amount': self.amount,
        }
        res = super().write(vals)

        data['new_type'] = self.type
        data['new_amount'] = self._calculate_amount()
        data['payscale_id'] = self.payscale_id.id

        self.env['hr.benefit.history'].create(data)
        return res

    @api.model_create_multi
    def create(self, values):
        if not values[0].get('employee_id', False):
            contract = self.env['hr.contract'].search([('id', '=', values[0]['contract_id'])])
            values[0]['employee_id'] = contract.employee_id and contract.employee_id.id or False
        res = super().create(values)
        if not res.salary_percentage_id:
            if res.allowance_id:
                for ap_line in res.allowance_id.percentage_ids:
                    if ap_line.domain:
                        if self.env['hr.employee'].search(safe_eval(ap_line.domain) + [('id', '=', res.employee_id.id)]):
                            res.salary_percentage_id = ap_line and ap_line.id or False
        return res


class HRSalaryAllowancesTemplate(models.Model):
    _name = "hr.salary.allowances.template"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Salary Allowances Template'

    name = fields.Char('Name', required=True, tracking=True)
    sequence = fields.Integer('Sequence')
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    template_lines = fields.Many2many('hr.salary.allowances', 'salary_allowances_template_rel', 'template_id', 'allowance_id', 'Allowances')
    remarks = fields.Text('Remarks')

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(HRSalaryAllowancesTemplate, self).unlink()


class HRSalaryDeductions(models.Model):
    _name = "hr.salary.deductions"
    _description = 'HR Salary Deductions'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    code = fields.Char('Code', tracking=True)

    percentage_type_id = fields.Many2one('hr.salary.percentage.type', 'Percentage Type')
    taxable = fields.Boolean('Taxable')
    percentage_ids = fields.One2many('hr.salary.percentage', 'deduction_id', 'DED Calculations')
    rule_ids = fields.One2many('hr.salary.rules', 'deduction_id', 'Salary rules')
    lines = fields.One2many('hr.emp.salary.deductions', 'deduction_id', 'Employees/Contracts', domain=[('expired', '=', False)])
    active = fields.Boolean('Active', default=True, tracking=True)
    date_start = fields.Date('Start Date', tracking=True)
    date_end = fields.Date('End Date', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    note = fields.Html('Note')

    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Deduction!"), ]

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            for rule in rec.rule_ids:
                if not rule.salary_rule_id and rec.code:
                    rule.create_salary_rule()
        return res

    def unlink(self):
        for rec in self:
            if rec.lines:
                raise ValidationError(_('Employees/structures are linked with Record'))
            if rec.rule_ids:
                raise ValidationError(_('Salary Rule is linked with Payroll Structure'))
        return super().unlink()

    @api.constrains('date_start', 'date_end')
    def date_period_constrains(self):
        for rec in self:
            if rec.date_end and rec.date_start and rec.date_start > rec.date_end:
                raise ValidationError(_('Date Start should be Before Date End'))

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    @api.onchange('active')
    def onchange_active_field(self):
        for rec in self:
            if not rec.active:
                emp_deductions = self.env['hr.emp.salary.deductions'].search([('deduction_id', '=', rec._origin.id)])
                if emp_deductions:
                    for emp_deduction in emp_deductions:
                        if emp_deduction.contract_id.state not in ('cancel', 'close'):
                            emp_deduction.write({'expired': True, 'expiry_date': fields.Date.today(),'expiry_amount':emp_deduction.amount})


class HREmpSalaryDeductions(models.Model):
    _name = "hr.emp.salary.deductions"
    _description = 'HR Salary Allowances'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    contract_id = fields.Many2one('hr.contract', 'Contract', compute='_get_contract', store=True)
    employee_id = fields.Many2one('hr.employee', 'Employee')
    payscale_id = fields.Many2one('hr.payscale', 'Payscale', compute='_get_contract', store=True, tracking=True)
    deduction_id = fields.Many2one('hr.salary.deductions', 'Deduction')
    code = fields.Char(related='deduction_id.code')

    type = fields.Selection([('fixed', 'Fixed'), ('formula', 'Formula')], 'Type', default='formula')
    amount_fixed = fields.Float('Fixed amt.', tracking=True)
    amount_formula = fields.Float(compute='calculate_amount', string='Formula amt', tracking=True)
    amount = fields.Float('Amount', tracking=True, compute='calculate_amount')

    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True, tracking=True)
    history_ids = fields.One2many('hr.benefit.history', 'deduction_id', 'History')
    expired = fields.Boolean('Expired', default=False)
    expiry_date = fields.Date('Expire Date')
    expiry_amount = fields.Float('Expiry Amount')
    salary_percentage_id = fields.Many2one('hr.salary.percentage', 'Salary Percentage')

    @api.depends('employee_id', 'deduction_id')
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, (rec.employee_id.name or '') + '/' + (rec.deduction_id.name or '')))
        return result

    @api.depends('employee_id')
    def _get_contract(self):
        for rec in self:
            if rec.employee_id:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], order='id desc', limit=1)
                rec.payscale_id = rec.employee_id.payscale_id and rec.employee_id.payscale_id.id or False
                # rec.contract_id = rec.employee_id.contract_ids and rec.employee_id.contract_ids[0].id or False
                rec.contract_id = contract_id and contract_id.id or False

    def _amount_formula(self):
        amount_formula = 0
        lines = []
        if self.salary_percentage_id:
            lines = self.salary_percentage_id
        for line in lines:
            if not line.domain or self.env['hr.employee'].search(safe_eval(line.domain) + [('id', '=', self.employee_id.id)]):
                if line.deduction_id.percentage_type_id.code=='IBP':
                    amount_formula = self.contract_id.basic_pay_initial * (line.value / 100)
                    if line.min_value > 0:
                        amount_formula = max(line.min_value, amount_formula)
                    if line.max_value > 0:
                        amount_formula = min(line.max_value, amount_formula)

                elif line.deduction_id.percentage_type_id.code=='RBP':
                    amount_formula = (self.contract_id.personal_pay_amount + self.contract_id.basic_pay) * (line.value / 100)
                    if line.min_value > 0:
                        amount_formula = max(line.min_value, amount_formula)
                    if line.max_value > 0:
                        amount_formula = min(line.max_value, amount_formula)

                elif line.deduction_id.percentage_type_id.code=='Fixed':
                    amount_formula = line.value
                break
        amount_formula = round(amount_formula)
        return amount_formula

    def calculate_amount(self):
        for rec in self:
            rec.amount_formula = rec._amount_formula()
            if rec.type=='fixed':
                rec.amount = rec.amount_fixed
                rec.amount_formula = 0
            else:
                rec.amount = rec.amount_formula
                rec.amount_fixed = 0

    def _calculate_amount(self):
        if self.type=='fixed':
            return self.amount_fixed
        else:
            return self._amount_formula()

    def write(self, vals):
        data = {
            'employee_id': self.employee_id.id,
            'allowance_id': False,
            'deduction_id': self.id,
            'date': datetime.now(),
            'type': self.type,
            'amount': self.amount,
        }
        res = super().write(vals)
        data['new_type'] = self.type
        data['new_amount'] = self._calculate_amount()
        data['payscale_id'] = self.payscale_id.id

        self.env['hr.benefit.history'].create(data)
        return res

    @api.model_create_multi
    def create(self, values):
        if not values[0].get('employee_id', False):
            contract = self.env['hr.contract'].search([('id', '=', values[0]['contract_id'])])
            values[0]['employee_id'] = contract.employee_id and contract.employee_id.id or False
        res = super().create(values)
        if not res.salary_percentage_id:
            if res.deduction_id:
                for dp_line in res.deduction_id.percentage_ids:
                    if dp_line.domain:
                        if self.env['hr.employee'].search(safe_eval(dp_line.domain) + [('id', '=', res.employee_id.id)]):
                            res.salary_percentage_id = dp_line and dp_line.id or False
        return res


class HRSalaryDeductionsTemplate(models.Model):
    _name = "hr.salary.deductions.template"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Salary Deductions Template'

    name = fields.Char('Name', required=True, tracking=True)
    sequence = fields.Integer('Sequence')
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    template_lines = fields.Many2many('hr.salary.deductions', 'salary_deductions_template_rel', 'template_id', 'deduction_id', 'Deductions')
    remarks = fields.Text('Remarks')

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(HRSalaryDeductionsTemplate, self).unlink()


class HREmpSalaryBenefitHistory(models.Model):
    _name = "hr.benefit.history"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Benefits History'
    _order = 'date desc'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    allowance_id = fields.Many2one('hr.emp.salary.allowances', 'Allowance', tracking=True)
    deduction_id = fields.Many2one('hr.emp.salary.deductions', 'Deduction', tracking=True)
    payscale_id = fields.Many2one('hr.payscale', 'Payscale')
    date = fields.Datetime('Date')

    type = fields.Selection([('fixed', 'Fixed'), ('formula', 'Formula')], 'Type', default='formula')
    amount = fields.Float('Amount', tracking=True)

    new_type = fields.Selection([('fixed', 'Fixed'), ('formula', 'Formula')], 'New Type', default='formula')
    new_amount = fields.Float('New Amount', tracking=True)


# There is no need of this class now
class HRBenefitChange(models.Model):
    _name = 'hr.benefit.change'
    _description = 'HR Benefit Change'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]},
        index=True, default=lambda self: _('New'))
    type = fields.Selection([('allowance', 'Allowance'), ('deduction', 'Deduction')], 'Type', required=1)
    date = fields.Date('Date')
    reason = fields.Text('Reason')
    allowance_id = fields.Many2one('hr.salary.allowances', string='Allowances')
    deduction_id = fields.Many2one('hr.salary.deductions', string='Deductions')
    line_ids = fields.One2many('hr.benefit.change.line', 'benefit_id', string='Lines')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved')], default='draft', string='State')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New'))==_('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.benefit.change') or _('New')
        result = super().create(vals)
        return result

    def action_approve(self):
        for rec in self.line_ids:
            employees = self.env['hr.employee'].search(
                [('payscale_id', '=', rec.payscale_id.id)])

            for emp in employees:
                contracts = self.env['hr.contract'].search(
                    [('employee_id', '=', emp.id)])
                if self.name=='allowance':
                    allowance = contracts.allowance_ids.filtered(lambda l: l.allowance_id.id==self.allowance_id.id)
                    if allowance:
                        allowance.amount = rec.new_amount
                if self.name=='deduction':
                    deduction = contracts.deduction_ids.filtered(lambda l: l.deduction_id.id==self.deduction_id.id)
                    if deduction:
                        deduction.amount = rec.new_amount

        self.state = 'approve'


class HRBenefitChangeLine(models.Model):
    _name = 'hr.benefit.change.line'
    _description = 'HR Benefit Change Line'

    benefit_id = fields.Many2one('hr.benefit.change', string='Change ID')
    payscale_id = fields.Many2one('hr.payscale', string='Payscale')
    new_amount = fields.Float('New Amount')


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    structure_ids = fields.Many2many('hr.payroll.structure', 'hr_structure_salary_rule_rel', 'rule_id', 'struct_id', string='Salary Structures')
