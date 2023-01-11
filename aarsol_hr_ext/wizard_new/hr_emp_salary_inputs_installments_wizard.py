import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class HREmpSalaryInputsInstallmentsWizard(models.TransientModel):
    _name = 'hr.emp.salary.inputs.installments.wizard'
    _description = 'Employee Salary Inputs Installments Wizard'

    def get_emp_salary_input(self):
        salary_input_rec = self.env['hr.emp.salary.inputs'].browse(self._context.get('active_id', False))
        return salary_input_rec and salary_input_rec.id or False

    def get_employee_id(self):
        salary_input_rec = self.env['hr.emp.salary.inputs'].browse(self._context.get('active_id', False))
        return salary_input_rec and salary_input_rec.employee_id.id or False

    def get_amount(self):
        salary_input_rec = self.env['hr.emp.salary.inputs'].browse(self._context.get('active_id', False))
        return salary_input_rec and salary_input_rec.amount or False

    employee_id = fields.Many2one('hr.employee', 'Employee', default=get_employee_id)
    emp_salary_input_id = fields.Many2one('hr.emp.salary.inputs', 'Allowance/Deduction', default=get_emp_salary_input)
    total_amount = fields.Float('Amount', required=True, default=get_amount)
    installments = fields.Integer('Installments', required=True)
    installment_amount = fields.Float('Installment Amount', compute='compute_installment_amount', store=True)
    start_date = fields.Date('Start Date For Next Installment', required=True)

    def action_create_entries(self):
        for rec in self:
            if rec.emp_salary_input_id.slip_id or rec.emp_salary_input_id.state=='done':
                raise UserError(_('This Records is already Process, you cannot Make installments of it.'))
            if rec.emp_salary_input_id:
                for i in range(0, rec.installments - 1):
                    dt = rec.start_date + relativedelta(months=i)
                    vals = {
                        'employee_id': rec.emp_salary_input_id.employee_id.id,
                        'name': rec.emp_salary_input_id.name,
                        'amount': rec.installment_amount,
                        'state': 'confirm',
                        'input_id': rec.emp_salary_input_id.input_id.id,
                        'date': dt,
                    }
                    self.env['hr.emp.salary.inputs'].create(vals)
                rec.emp_salary_input_id.amount = rec.installment_amount
                rec.emp_salary_input_id.message_post(body="Installments Created")
        return {'type': 'ir.actions.act_window_close'}

    @api.constrains("start_date")
    def start_date_constrains(self):
        for rec in self:
            if rec.start_date and rec.emp_salary_input_id:
                if rec.start_date < rec.emp_salary_input_id.date:
                    raise UserError(_('Start Date Should be Greater then Main Record Date.'))

    @api.depends('installments', 'total_amount')
    def compute_installment_amount(self):
        for rec in self:
            if rec.installments > 0:
                rec.installment_amount = round(rec.total_amount / rec.installments)
