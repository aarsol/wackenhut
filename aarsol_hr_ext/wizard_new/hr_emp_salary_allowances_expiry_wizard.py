import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class HREmpSalaryAllowancesExpiryWizard(models.TransientModel):
    _name = 'hr.emp.salary.allowances.expiry.wizard'
    _description = 'This Wizard Will Expire the Employee/Contracts in the Selected Allowance'

    def get_allowance_id(self):
        allowance_rec = False
        if self._context.get('active_model', False)=='hr.salary.allowances' and self._context.get('active_id', False):
            allowance_rec = self.env['hr.salary.allowances'].browse(self._context.get('active_id', False))
        return allowance_rec and allowance_rec.id or False

    def get_deduction_id(self):
        deduction_rec = False
        if self._context.get('active_model', False)=='hr.salary.deductions' and self._context.get('active_id', False):
            deduction_rec = self.env['hr.salary.deductions'].browse(self._context.get('active_id', False))
        return deduction_rec and deduction_rec.id or False

    allowance_id = fields.Many2one('hr.salary.allowances', 'Allowance', default=get_allowance_id)
    deduction_id = fields.Many2one('hr.salary.deductions', 'Deduction', default=get_deduction_id)
    date = fields.Date('Date', default=fields.Date.today())
    percentage_ids = fields.Many2many('hr.salary.percentage', 'hr_emp_salary_alw_expiry_percentage_rel1', 'wiz', 'percentage_id', 'Calculations')

    def action_expiry_allowances(self):
        for rec in self:
            if rec.allowance_id:
                if not rec.percentage_ids:
                    raise UserError(_('Please Select the Records.'))
                employee_ids = self.env['hr.employee'].search([])
                for employee_id in employee_ids:
                    employee_contract = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)], order='id desc', limit=1)
                    if employee_contract:
                        for percentage_id in rec.percentage_ids:
                            if percentage_id.domain:
                                if self.env['hr.employee'].search(safe_eval(percentage_id.domain) + [('id', '=', employee_id.id)]):
                                    employee_allowance = employee_contract.allowance_ids.filtered(lambda alw: alw.allowance_id.code==rec.allowance_id.code)
                                    if employee_allowance:
                                        employee_allowance.expired = True
                                        employee_allowance.expiry_date = rec.date
                                        employee_allowance.expiry_amount = employee_allowance.amount

            if rec.deduction_id:
                if not rec.percentage_ids:
                    raise UserError(_('Please Select the Records.'))
                employee_ids = self.env['hr.employee'].search([])
                for employee_id in employee_ids:
                    employee_contract = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)], order='id desc', limit=1)
                    if employee_contract:
                        for percentage_id in rec.percentage_ids:
                            if percentage_id.domain:
                                if self.env['hr.employee'].search(safe_eval(percentage_id.domain) + [('id', '=', employee_id.id)]):
                                    employee_deduction = employee_contract.deduction_ids.filtered(lambda ded: ded.deduction_id.code==rec.deduction_id.code)
                                    if employee_deduction:
                                        employee_deduction.expired = True
                                        employee_deduction.expiry_date = rec.date
                                        employee_deduction.expiry_amount = employee_deduction.amount

        return {'type': 'ir.actions.act_window_close'}
