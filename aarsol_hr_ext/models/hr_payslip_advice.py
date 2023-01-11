import pdb
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class PayrollAdvice(models.Model):
    _name = 'hr.payroll.advice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Bank Advice'

    name = fields.Char('Name', readonly=True, required=False, states={'draft': [('readonly', False)]}, tracking=True)
    note = fields.Text('Description', default='Please make the payroll transfer from above account number to the below mentioned account numbers towards employee salaries:', tracking=True)
    date = fields.Date('Date', readonly=True, required=True, states={'draft': [('readonly', False)]}, help="Advice Date is used to search Payslips", tracking=True, default=fields.Date.today())
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('cancel', 'Cancelled'),
                              ], 'Status', index=True, readonly=True, default='draft', tracking=True)
    number = fields.Char('Reference', readonly=True, tracking=True)
    line_ids = fields.One2many('hr.payroll.advice.line', 'advice_id', 'Employee Salary', states={'draft': [('readonly', False)]}, readonly=True, copy=True)
    cheque_nos = fields.Char('Cheque Numbers', tracking=True)
    neft = fields.Boolean('NEFT Transaction', help="Check this box if your company use online transfer for salary", tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id)
    bank_id = fields.Many2one('res.partner.bank', 'Bank', readonly=True, states={'draft': [('readonly', False)]}, help="Select the Bank from which the Salary is going to be Paid", tracking=True)
    batch_id = fields.Many2one('hr.payslip.run', 'Batch', readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    total = fields.Float('Total', compute='compute_total', store=True, tracking=True)
    send_sms = fields.Boolean('Sent SMS?', default=False, tracking=True)
    send_email = fields.Boolean('Sent Email?', default=False, tracking=True)

    @api.depends('line_ids', 'batch_id')
    def compute_total(self):
        for rec in self:
            total = 0
            for ln in rec.line_ids:
                total += ln.bysal
            rec.total = total

    def compute_advice(self):
        """ Advice - Create Advice lines in Payment Advice and compute Advice lines."""
        for advice in self:
            old_lines = self.env['hr.payroll.advice.line'].search([('advice_id', '=', advice.id)])
            if old_lines:
                old_lines.unlink()
            # payslips = self.env['hr.payslip'].search([('date_from', '<=', advice.date), ('date_to', '>=', advice.date), ('state', '=', 'done'),('payslip_run_id','=',advice.batch_id.id)])
            payslips = self.env['hr.payslip'].search([('state', '=', 'done'), ('payslip_run_id', '=', advice.batch_id.id)])
            for slip in payslips:
                # if not slip.employee_id.bank_account_id and not slip.employee_id.bank_account_id.acc_number:

                ##For testing
                # if not slip.employee_id.bank_id and not slip.employee_id.bankacc:
                #	raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name,))

                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                if payslip_line:
                    advice_line = {
                        'advice_id': advice.id,
                        'name': slip.employee_id.bankacc and slip.employee_id.bankacc or '',
                        'account_title': slip.employee_id.bankacctitle and slip.employee_id.bankacctitle or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total,
                        'slip_id': slip.id,

                    }
                    self.env['hr.payroll.advice.line'].create(advice_line)
                slip.advice_id = advice.id

        # Override Advice Name
        if advice.batch_id:
            batch_name = advice.batch_id.name and advice.batch_id.name or False
            if batch_name:
                advice.name = batch_name.replace('BAT', "ADV")

    def send_payslip_sms(self):
        for rec in self:
            # Here Please Check that SEND SMS is True, if True Then do not Send the SMS,
            # if not rec.slip_id.send_sms:
            text = rec.prepare_message_text(rec)
            message = self.env['send_sms'].render_template(text, 'hr.payslip', rec.id)
            mobile_no = (rec.employee_id.mobile_phone and rec.employee_id.mobile_phone) or (
                    rec.employee_id.work_phone and rec.employee_id.work_phone) or False
            gatewayurl_id = self.env['gateway_setup'].search([('id', '=', 1)])

            if mobile_no:
                mobile_no = mobile_no.replace(' ', '')
                mobile_no = mobile_no.replace('-', '')
                if mobile_no[0]=='0':
                    mobile_no = '92' + mobile_no[1:11]
                else:
                    mobile_no = mobile_no
                self.env['send_sms'].send_sms_link(message, mobile_no, rec.id, 'hr.payslip', gatewayurl_id)
            # rec.slip_id.send_sms = True

    def prepare_message_text(self, slip=False):
        message = ''
        if slip:
            slip_month = slip.date_to.strftime('%B-%Y')
            gross_salary = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'GROSS')])
            net_salary = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')])
            deduction_lines = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('category_id', '=', 4), ('total', '<', -1)])

            # self.env.cr.execute ("""select sum(abs(ln.total)) as total,cat.name as name from hr_payslip_line ln, hr_salary_rule_category cat where ln.slip_id=%s and ln.category_id = cat.id group by ln.category_id,cat.name order by ln.category_id""" %(slip.id))
            # result = self.env.cr.dictfetchall()

            message = "Dear ERP." + slip.employee_id.code + ", Your Salary For the Month of " + slip_month + " has been transferred to the A/c No." + slip.bankacc + "\n Detail is as \n Gross Salary: " + str(gross_salary.total) + '\n Deduction Details'
            if deduction_lines:
                for deduction_line in deduction_lines:
                    message = message + " \n" + deduction_line.name + ": " + str(abs(deduction_line.total))
            message = message + "\n Net Salary : " + str(net_salary.total)
            message = message + "\n Regards: SOS"
        else:
            message = ''
        return message

    def send_payslip_email(self):
        for rec in self:
            if rec.batch_id and rec.batch_id.slip_ids:
                for slip in rec.batch_id.slip_ids:
                    if not slip.send_email:
                        slip.send_payslip_email()
                rec.send_email = True

    def confirm_sheet(self):
        """confirm Advice - confirmed Advice after computing Advice Lines.."""
        for advice in self:
            if not advice.line_ids:
                raise UserError(_('You can not confirm Payment advice without advice lines.'))
            advice_date = fields.Date.from_string(fields.Date.today())
            advice_year = advice_date.strftime('%m') + '-' + advice_date.strftime('%Y')
            number = self.env['ir.sequence'].next_by_code('payment.advice')
            sequence_num = 'PAY' + '/' + advice_year + '/' + number
            advice.write({
                'number': sequence_num,
                'state': 'confirm'
            })

    def set_to_draft(self):
        self.write({'state': 'draft'})

    def cancel_sheet(self):
        self.write({'state': 'cancel'})

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.bank_id = self.company_id.partner_id.bank_ids and self.company_id.partner_id.bank_ids[0].bank_id.id or False


class PayrollAdviceLine(models.Model):
    _name = 'hr.payroll.advice.line'
    _description = 'Bank Advice Lines'

    advice_id = fields.Many2one('hr.payroll.advice', 'Bank Advice')
    name = fields.Char('Bank Account No.', size=25, required=True)
    account_title = fields.Char('Account Title')
    ifsc_code = fields.Char('IFSC Code', size=16)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    bysal = fields.Float('By Salary')
    debit_credit = fields.Char('C/D', size=3, required=False, default='C')
    company_id = fields.Many2one('res.company', 'Company', related='advice_id.company_id', required=False, store=True)
    ifsc = fields.Boolean('IFSC', related='advice_id.neft')
    slip_id = fields.Many2one('hr.payslip', 'PaySlip')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.name = self.employee_id.bank_account_id.acc_number
        self.ifsc_code = self.employee_id.bank_account_id.bank_bic or ''
