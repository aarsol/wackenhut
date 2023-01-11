import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class HRInputsWizard(models.TransientModel):
    _name = 'hr.inputs.wizard'
    _description = 'Inputs Wizard'

    input_rule = fields.Many2one('hr.salary.inputs', 'Category', required=True)
    input_code = fields.Char('Code', related='input_rule.code', store=True)
    payscale_ids = fields.Many2many('hr.payscale', 'hr_input_payscale_rel', 'wiz_id', 'payscale_id', 'Payscales')
    total_amount = fields.Float('Amount', required=True)
    installments = fields.Integer('Installments', required=True)
    installment_amount = fields.Float('Installment Amount', compute='compute_installment_amount', store=True)
    start_date = fields.Date('Start Date', required=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_inputs_employee_rel', 'wiz_id', 'emp_id', 'Employee')

    def action_create_entries(self):
        for rec in self:
            if rec.payscale_ids:
                employees = self.env['hr.employee'].search([('payscale_id', 'in', rec.payscale_ids.ids), ('id', 'not in', rec.employee_ids.ids)])
            # else:
            #     employees = rec.employee_ids

            if employees:
                for employee in employees:
                    for i in range(0, rec.installments):
                        date = rec.start_date + relativedelta(months=i)
                        vals = {
                            'employee_id': employee.id,
                            'input_id': rec.input_rule.id,
                            'date': date,
                            'amount': rec.installment_amount,
                            'state': 'draft',
                        }
                        self.env['hr.emp.salary.inputs'].create(vals)
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('installments', 'total_amount')
    def compute_installment_amount(self):
        for rec in self:
            if rec.installments > 0:
                rec.installment_amount = rec.total_amount / rec.installments
