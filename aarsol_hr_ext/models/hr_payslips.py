from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from collections import defaultdict
from odoo.tools import date_utils
from odoo.tools.misc import format_date
from odoo.tools import float_compare, float_is_zero, float_round
from dateutil.relativedelta import relativedelta
import pdb

import logging

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payscale_id = fields.Many2one('hr.payscale', related='employee_id.payscale_id', string='Payscale', store=True)
    designation_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Designation', store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department', store=True)
    section_id = fields.Many2one('hr.section', related='employee_id.section_id', string='Section', store=True)
    top_sheet_category_id = fields.Many2one('top.sheet.category', related='employee_id.section_id.top_sheet_category_id', string='Top Sheet Category', store=True)
    slip_max_days = fields.Integer('Slip Max Days', compute='compute_slip_max_days', store=True)
    slip_month = fields.Char('Slip Month', compute='_compute_slip_month', store=True)

    bank_account_title = fields.Char('Account Title')
    bank_account_no = fields.Char('Account No')
    hr_bank_id = fields.Many2one('hr.bank', 'Bank')
    bank_location = fields.Char('Bank Location', tracking=True)
    bank_branch = fields.Char('Bank Branch', tracking=True)
    payment_mode = fields.Selection([('bank', 'Bank'),
                                     ('cash', 'Cash'),
                                     ('cheque', 'Cheque'),
                                     ('demand_draft', 'Demand Draft'),
                                     ], default='bank', string='Payment Mode', tracking=True, groups="hr.group_hr_user")


    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = []
        arrears_obj = self.env['hr.emp.salary.inputs']
        structures = contracts.structure_type_id.default_struct_id
        if structures and structures.input_line_type_ids:
            for rule_id in structures.input_line_type_ids:
                emp_salary_input_id = False
                arr_amt = ''
                arr_ids = arrears_obj.search(
                    [('employee_id', '=', contracts.employee_id.id), ('name', '=', rule_id.code),
                     ('date', '>=', date_from), ('date', '<=', date_to), ('state', '=', 'confirm')])
                if arr_ids:
                    arr_amt = 0
                    for arr_id in arr_ids:
                        emp_salary_input_id = arr_id.id
                        arr_amt += arr_id.amount
                inputs = {
                    'name': rule_id.name,
                    'code': rule_id.code,
                    'contract_id': contracts.id,
                    'amount': arr_amt or 0,
                    'input_type_id': rule_id.id,
                    'emp_salary_input_id': emp_salary_input_id,
                }
                res += [inputs]
        return res

    @api.model
    def get_inputs2(self, contracts, date_from, date_to):
        res = []
        rule_obj = self.env['hr.salary.rule']
        arrears_obj = self.env['hr.salary.inputs']
        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        for contract in contracts:
            for rule in rule_obj.browse(sorted_rule_ids):
                if rule.input_ids:
                    for input in rule.input_ids:
                        arr_amt = ''
                        arr_ids = arrears_obj.search([('employee_id', '=', contract.employee_id.id),
                                                      ('name', '=', input.code),
                                                      ('date', '>=', date_from),
                                                      ('date', '<=', date_to),
                                                      ('state', '=', 'confirm')])
                        if arr_ids:
                            arr_amt = 0
                            for arr_id in arr_ids:
                                arr_amt += arr_id.amount
                        inputs = {
                            'name': input.name,
                            'code': input.code,
                            'contract_id': contract.id,
                            'amount': arr_amt or 0,
                        }
                        res += [inputs]
        return res

    @api.model
    def get_contract(self, employee, date_from, date_to):
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', 'in', ('draft', 'open')), '|', '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        if self.employee_id.payroll_status=='stop':
            salary_stop_request = self.env['hr.employee.payroll.status'].search([('employee_id', '=', self.employee_id.id),
                                                                                 ('payroll_status', '=', 'stop')], order='id desc', limit=1)
            if salary_stop_request and not (self.date_from < salary_stop_request.date < self.date_to):
                return

        if self.employee_id.payroll_status=='start':
            salary_start_request = self.env['hr.employee.payroll.status'].search([('employee_id', '=', self.employee_id.id),
                                                                                  ('payroll_status', '=', 'start')], order='id desc', limit=1)
            if salary_start_request and not (self.date_from < salary_start_request.date < self.date_to):
                return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        self.payment_mode = employee.payment_mode
        self.hr_bank_id = employee.hr_bank_id and employee.hr_bank_id.id or False
        self.bank_account_title = employee.bank_account_title
        self.bank_account_no = employee.bank_account_no
        self.bank_branch = employee.bank_branch

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id!=self.contract_id.employee_id:  # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        self.name = '%s - %s - %s' % (
            payslip_name, self.employee_id.name.title() or '', format_date(self.env, self.date_from, date_format="MMMM y"))
        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False
        # self.worked_days_line_ids = self._get_new_worked_days_lines()
        self.worked_days_line_ids = self._get_worked_day_lines_values_aarsol()
        if self.contract_id:
            self.input_line_ids = self._get_new_input_lines(self.contract_id, date_from, date_to)

    def _get_new_input_lines(self, contract, date_from, date_to):
        input_line_values = self.get_inputs(contract, date_from, date_to)
        if input_line_values:
            input_lines = self.input_line_ids.browse([])
            for r in input_line_values:
                input_lines |= input_lines.new(r)
            return input_lines
        else:
            return [(5, False, False)]

    # Get the total Days and Month Days from Custom Table Month Attendance
    def _get_worked_day_lines_values_aarsol(self):
        res = []
        total_leaves = 0
        attendance_days = 0
        # fill only if the contract as a working schedule linked
        self.ensure_one()

        max_work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'MAX')])
        # MAX Work Dict, it contains to month days
        attendance_line = {
            'sequence': 10,
            'work_entry_type_id': max_work_entry_type.id,
            'number_of_days': self.date_to.day,
            'number_of_hours': self.date_to.day * 8,
        }
        res.append(attendance_line)
        attendance_policy = self.env['ir.config_parameter'].sudo().get_param('aarsol_hr_ext.attendance_policy')
        if not attendance_policy:
            raise UserError(_('Please Define the Attendance Policy from Payroll Setting.\n Currently no Policy is Selected.'))

        if attendance_policy=='bio':
            if self.contract_id and self.contract_id.date_start > self.date_from:
                attendance_days = (self.date_to - self.contract_id.date_start).days
            if attendance_days==0:
                attendance_recs = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id),
                                                                    ('check_in', '>=', self.date_from),
                                                                    ('check_out', '<=', self.date_to)])
                attendance_days = len(attendance_recs)

        if attendance_policy=='monthly':
            # if contract start Date is Greater than Payslip From Date
            # e.g contract Start Date is 15-01-2021 and Payslip From Date is 01-01-2021
            # System should give the preference to the Contract Days

            att_flag = False
            if not self.employee_id.re_appointed and self.employee_id.retirement_date and self.employee_id.retirement_date < self.date_from:
                att_flag = True
            elif not self.employee_id.re_appointed and self.employee_id.retirement_date and self.date_from < self.employee_id.retirement_date < self.date_to:
                attendance_days = self.employee_id.retirement_date.day
            elif self.employee_id.payroll_status=='stop':
                salary_stop_request = self.env['hr.employee.payroll.status'].search([('employee_id', '=', self.employee_id.id),
                                                                                     ('payroll_status', '=', 'stop')], order='id desc', limit=1)
                if salary_stop_request and self.date_from < salary_stop_request.date < self.date_to:
                    attendance_days = salary_stop_request.date.day
                else:
                    if self.contract_id.date_end and self.date_from < self.contract_id.date_end < self.date_to:
                        attendance_days = self.contract_id.date_end.day

            # Payroll Stop Handling
            elif self.employee_id.payroll_status=='start':
                salary_start_request = self.env['hr.employee.payroll.status'].search([('employee_id', '=', self.employee_id.id),
                                                                                      ('payroll_status', '=', 'start')], order='id desc', limit=1)
                if salary_start_request and self.date_from < salary_start_request.date < self.date_to:
                    attendance_days = ((self.date_to - salary_start_request.date).days + 1)
                else:
                    if self.contract_id.date_end and self.date_from < self.contract_id.date_end < self.date_to:
                        attendance_days = self.contract_id.date_end.day
                    elif self.date_from > self.contract_id.date_start:
                        attendance_days = (self.date_to - self.date_from).days + 1
                    else:
                        attendance_days = (self.date_to - self.contract_id.date_start).days + 1
            elif self.contract_id.date_end and self.date_from < self.contract_id.date_end < self.date_to:
                attendance_days = self.contract_id.date_end.day

            else:
                if self.contract_id and self.contract_id.date_start > self.date_from:
                    if self.contract_id.date_start==self.contract_id.first_contract_date:
                        attendance_days = (self.date_to - self.contract_id.date_start).days + 1
                    else:
                        attendance_days = (self.date_to - self.contract_id.date_start).days + 1

                    #     prev_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                    #                                                     ('date_end', '>=', self.date_from),
                    #                                                     ('date_end', '<=', self.date_to),
                    #                                                     ('state', '=', 'close')], order='id desc', limit=1)
                    #     if prev_contract:
                    #         attendance_days = (attendance_days + (prev_contract.date_end - self.date_from).days) + 1

            # If Contract Start Date is Smaller then Payslip From Date
            # e.g Contract Start is 01-07-2020 and Payslip From Date is 01-01-2021
            # System first will check it in the Month Attendance Table
            # other Wise Pick Payslip To Date, Days

            if attendance_days==0 and not att_flag:
                attendance_rec = self.env['hr.employee.month.attendance'].search([('employee_id', '=', self.employee_id.id),
                                                                                  ('date', '>=', self.date_from),
                                                                                  ('date', '<=', self.date_to),
                                                                                  ], order='id desc', limit=1)
                if attendance_rec:
                    attendance_days = attendance_rec.present_days

            if attendance_days==0 and not att_flag:
                attendance_days = int(self.date_to.strftime("%d"))

        if attendance_days > 0:
            work_entry_type = self.env['hr.work.entry.type'].search([('id', '=', 1)])
            attendance_line = {
                'sequence': 20,
                'work_entry_type_id': work_entry_type.id,
                'number_of_days': attendance_days,
                'number_of_hours': attendance_days * 8,
            }
            res.append(attendance_line)

        # Employee Leaves Management
        unpaid_time_off_recs = self.env['hr.leave'].search([('employee_id', '=', self.employee_id.id),
                                                            ('request_date_from', '>=', self.date_from),
                                                            ('request_date_to', '<=', self.date_to),
                                                            ('state', '=', 'validate'),
                                                            ('holiday_status_id.unpaid', '=', True)])
        if unpaid_time_off_recs:
            for unpaid_time_off_rec in unpaid_time_off_recs:
                total_leaves += unpaid_time_off_rec.number_of_days
                attendance_line = {
                    'sequence': 50,
                    'work_entry_type_id': unpaid_time_off_rec.holiday_status_id.work_entry_type_id.id,
                    'number_of_days': unpaid_time_off_rec.number_of_days,
                    'number_of_hours': unpaid_time_off_rec.number_of_days * 8,
                }
                res.append(attendance_line)

            # At res[1], there is the Working Days Attendance
            res[1]['number_of_days'] -= total_leaves
            res[1]['number_of_hours'] -= total_leaves * 8
        if res:
            worked_day_lines = self.worked_days_line_ids.browse([])
            for r in res:
                worked_day_lines |= worked_day_lines.new(r)
            return worked_day_lines
        return [(5, False, False)]

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()

            # Handling Arrears for Recompute
            p_arr_ids = self.env['hr.emp.salary.inputs'].search([('employee_id', '=', payslip.employee_id.id),
                                                                 ('date', '>=', payslip.date_from),
                                                                 ('date', '<=', payslip.date_to),
                                                                 ('state', '!=', 'cancel')])
            for p_arr_id in p_arr_ids:
                emp_salary_input_id = payslip.input_line_ids.filtered(lambda l: l.emp_salary_input_id.id==p_arr_id.id)
                if emp_salary_input_id:
                    emp_salary_input_id.amount = p_arr_id.amount
                if not emp_salary_input_id:
                    payslip_inp_rec = payslip.input_line_ids.filtered(lambda aa: aa.input_type_id.name==p_arr_id.input_id.name)
                    if payslip_inp_rec:
                        payslip_inp_rec.amount = p_arr_id.amount

            # Changing Loans Status
            arr_ids = self.env['hr.emp.salary.inputs'].search([('employee_id', '=', payslip.employee_id.id),
                                                               ('date', '>=', payslip.date_from),
                                                               ('date', '<=', payslip.date_to),
                                                               ('state', '=', 'confirm')])
            if arr_ids:
                loan_line_ids = self.env['hr.loan.line'].search([('salary_input_id', 'in', arr_ids.ids)])
                if loan_line_ids:
                    loan_line_ids.write({'paid': True})

            arr_ids.write({'state': 'done', 'slip_id': payslip.id})
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]

            # Back Date Arrears Handling Head Wise
            bba_ids = self.env['hr.employee.backdate.arrears'].search([('employee_id', '=', payslip.employee_id.id),
                                                                       ('slip_month', '>=', payslip.date_from),
                                                                       ('slip_month', '<=', payslip.date_to),
                                                                       ('state', '=', 'confirm'),
                                                                       ('ttype', '=', 'deduction')])
            if bba_ids:
                for bba_id in bba_ids:
                    for bba_deduction in bba_id.deduction_ids:
                        deduction_salary_rule_id = bba_deduction.rule_ids and bba_deduction.rule_ids[0] or False
                        if deduction_salary_rule_id:
                            for ln in lines:
                                emp_salary_deduction_id = self.env['hr.emp.salary.deductions'].search([('employee_id', '=', payslip.employee_id.id),
                                                                                                       ('contract_id', '=', payslip.contract_id.id),
                                                                                                       ('deduction_id', '=', bba_deduction.id)])
                                if ln[2]['salary_rule_id']==deduction_salary_rule_id.salary_rule_id.id:
                                    month_last_date = payslip.date_from + relativedelta(day=31)
                                    worked_days = payslip.worked_days_line_ids.filtered(lambda dd: dd.work_entry_type_id.code=='WORK100')
                                    ln[2]['amount'] = ln[2]['amount'] - (bba_id.calc_salary_head_amount(emp_salary_deduction_id) / int(worked_days.number_of_days))
                                    # ln[2]['amount'] = ln[2]['amount'] - (bba_id.calc_salary_head_amount(emp_salary_deduction_id) / int(month_last_date.strftime('%d')))

            payslip.write({'line_ids': lines,
                           'number': number,
                           'state': 'verify',
                           'compute_date': fields.Date.today()})

            # # For SMS
            # if not payslip.send_sms:
            #     slip_month = (tools.ustr(ttyme.strftime('%B-%Y')))
            #     text = "Dear Mr./Ms. " + payslip.employee_id.name + ", \n Your Salary For the Month of " + slip_month + " has been Generated. \n Regards, SOS."
            #     message = self.env['send_sms'].render_template(text, 'hr.payslip', payslip.id)
            #     mobile_no = (payslip.employee_id.mobile_phone and payslip.employee_id.mobile_phone) or (
            #             payslip.employee_id.work_phone and payslip.employee_id.work_phone) or False
            #     gatewayurl_id = self.env['gateway_setup'].search([('id', '=', 1)])
            # # if mobile_no:
            # #	self.env['send_sms'].send_sms_link(message, mobile_no, payslip.id, 'hr.payslip', gatewayurl_id)
        return True

    def action_payslip_done(self):
        if not self.env.context.get('without_compute_sheet'):
            for rec in self:
                rec.compute_sheet()
                template = self.env.ref('aarsol_hr_ext.email_template_payslip', raise_if_not_found=False)
                template.send_mail(rec.id,
                                   force_send=True,
                                   raise_exception=False,
                                   email_values={'email_to': rec.employee_id.work_email or rec.employee_id.private_email, 'recipient_ids': []},
                                   )
                rec.write({'state': 'done'})

    @api.depends('date_from')
    def compute_slip_max_days(self):
        for rec in self:
            max_days = 0
            if rec.date_to:
                max_days = int(rec.date_to.strftime('%d'))
            rec.slip_max_days = max_days

    def action_payslip_cancel(self):
        super(HrPayslip, self).action_payslip_cancel()
        for slip in self:
            salary_inputs = self.env['hr.emp.salary.inputs'].search([('slip_id', '=', slip.id)])
            if salary_inputs:
                salary_inputs.write({'slip_id': False, 'state': 'confirm'})

    @api.depends('date_to')
    def _compute_slip_month(self):
        for rec in self:
            if rec.date_to:
                rec.slip_month = rec.date_to.strftime('%B %Y')

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'employee_id' not in values or 'contract_id' not in values:
                payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
                values['employee_id'] = values.get('employee_id') or payslip.employee_id.id
                values['contract_id'] = values.get('contract_id') or payslip.contract_id and payslip.contract_id.id
                if not values['contract_id']:
                    raise UserError(_('You must set a contract to create a payslip line.'))

            # add @16-11-2021
            if values.get('employee_id', False):
                employee_rec = self.env['hr.employee'].search([('id', '=', values['employee_id'])])
                values['payment_mode'] = employee_rec.payment_mode
                values['hr_bank_id'] = employee_rec.hr_bank_id and employee_rec.hr_bank_id.id or False
                values['bank_account_title'] = employee_rec.bank_account_title
                values['bank_account_no'] = employee_rec.bank_account_no
                values['bank_branch'] = employee_rec.bank_branch

            # Added at 08-08-2021
            # Check the Duplicate Payslips
            already_exit = self.env['hr.payslip'].search([('employee_id', '=', values['employee_id']), ('date_from', '>=', values['date_from']), ('date_to', '<=', values['date_to'])], order='id desc', limit=1)
            if already_exit and not already_exit.state=='cancel':
                employee_rec = self.env['hr.employee'].search([('id', '=', values['employee_id'])])
                raise UserError(_('💥Information!\nPayslip of Employee %s - %s \nfrom %s to %s is already Available in the System.\nSlip Reference is %s')
                                % (employee_rec.code, employee_rec.name, values['date_from'], values['date_to'], already_exit.number))

        return super(HrPayslip, self).create(vals_list)


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = round(float(line.quantity) * line.amount * line.rate / 100)
