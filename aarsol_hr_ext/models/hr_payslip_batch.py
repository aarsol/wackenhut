import pdb
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class HRPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread', 'mail.activity.mixin']
    _description = 'Payslip Batches'

    state = fields.Selection([('draft', 'Draft'),
                              ('close', 'Close')
                              ], string='Status', index=True, readonly=True, copy=False, default='draft', tracking=True)
    available_advice = fields.Boolean('Made Payment Advice?', help="If this box is checked which means that Payment Advice exists for current batch", readonly=False, copy=False)
    total = fields.Float('Total', compute='compute_total')

    def draft_payslip_run(self):
        super(HRPayslipRun, self).draft_payslip_run()
        self.write({'available_advice': False})

    @api.depends('slip_ids')
    def compute_total(self):
        for rec in self:
            total = 0
            for slip in rec.slip_ids:
                total += slip.total
            rec.total = total

    def create_advice(self):
        for run in self:
            if run.available_advice:
                raise UserError(_("Payment Advice Already Exists For %s, 'Set to Draft' to Create a New Advice.") % (run.name,))
            company = self.env.user.company_id
            advice_data = {
                'batch_id': run.id,
                'company_id': company.id,
                'name': run.name,
                'date': run.date_end,
                'bank_id': company.partner_id.bank_ids and company.partner_id.bank_ids[0].id or False
            }
            advice = self.env['hr.payroll.advice'].create(advice_data)
            for slip_id in run.slip_ids:
                # TODO is it necessary to interleave the calls ?
                slip_id.action_payslip_done()

                # 14082022@sarfraz
                # if not slip_id.employee_id.bank_account_id or not slip_id.employee_id.bank_account_id.acc_number:
                #     raise UserError(_('Please define bank account for the %s employee') % (slip_id.employee_id.name))

                if slip_id.employee_id.payment_mode=='bank' and not slip_id.employee_id.bank_account_no:
                    raise UserError(_('Please define bank account for the %s employee') % (slip_id.employee_id.name))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip_id.id), ('code', '=', 'NET')], limit=1)
                if payslip_line:
                    advice_line = {
                        'advice_id': advice.id,
                        'name': slip_id.employee_id.bank_account_no and slip_id.employee_id.bank_account_no or '',
                        # 'ifsc_code': slip.employee_id.bank_account_id.bank_bic or '',
                        'employee_id': slip_id.employee_id.id,
                        'account_title': slip_id.employee_id.bank_account_title and slip_id.employee_id.bank_account_title or '',
                        'bysal': payslip_line.total
                    }
                    self.env['hr.payroll.advice.line'].create(advice_line)
        self.write({'available_advice': True})
