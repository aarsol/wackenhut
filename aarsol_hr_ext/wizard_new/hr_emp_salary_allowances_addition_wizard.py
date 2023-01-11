import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class HREmpSalaryAllowancesAdditionWizard(models.TransientModel):
    _name = 'hr.emp.salary.allowances.addition.wizard'
    _description = 'This Wizard Will Add the Employee/Contracts in the Selected Allowance'

    def get_allowance_id(self):
        allowance_rec = self.env['hr.salary.allowances'].browse(self._context.get('active_id', False))
        return allowance_rec and allowance_rec.id or False

    allowance_id = fields.Many2one('hr.salary.allowances', 'Allowance', default=get_allowance_id)
    percentage_ids = fields.Many2many('hr.salary.percentage', 'hr_emp_salary_alw_addition_percentage_rel1', 'wiz', 'percentage_id', 'Calculations')
    employee_ids = fields.Many2many('hr.employee', 'hr_emp_salary_alw_addition_emp_rel', 'salary_alw_wiz_id', 'employee_id')

    def action_add_contracts(self):
        for rec in self:
            if rec.allowance_id:
                new_emp_salary_alw_rec = False
                if not rec.percentage_ids:
                    raise UserError(_('Please Select the Employee(s).'))
                employee_ids = self.env['hr.employee'].search([])
                for employee_id in employee_ids:
                    employee_contract = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)], order='id desc', limit=1)
                    # if not employee_contract:
                    #     raise UserError(_('Contract for Employee %s-%s not found in the System please First Define Contract then try it.') % (employee_id.code, employee_id.name))
                    already_exists = self.env['hr.emp.salary.allowances'].search([('employee_id', '=', employee_id.id),
                                                                                  ('contract_id', '=', employee_contract.id),
                                                                                  ('allowance_id', '=', rec.allowance_id.id),
                                                                                  ('expired', '=', False)])
                    if not already_exists:
                        salary_percentage_id = False
                        alw_flag = False
                        for percentage_id in rec.percentage_ids:
                            if percentage_id.domain:
                                if self.env['hr.employee'].search(safe_eval(percentage_id.domain) + [('id', '=', employee_id.id)]):
                                    alw_flag = True
                                    salary_percentage_id = percentage_id
                            if not alw_flag and not percentage_id.domain and percentage_id.value > 0:
                                alw_flag = True

                        if alw_flag:
                            hr_emp_salary_alw_values = {
                                'employee_id': employee_id.id,
                                'contract_id': employee_contract.id,
                                'allowance_id': rec.allowance_id.id,
                                'payscale_id': employee_id.payscale_id and employee_id.payscale_id.id or False,
                                'salary_percentage_id': salary_percentage_id and salary_percentage_id.id or False,
                            }
                            new_emp_salary_alw_rec = self.env['hr.emp.salary.allowances'].create(hr_emp_salary_alw_values)
                            # Not Add if Zeros
                            if new_emp_salary_alw_rec and new_emp_salary_alw_rec.amount==0 and new_emp_salary_alw_rec.amount_fixed==0 and new_emp_salary_alw_rec.amount_formula==0:
                                new_emp_salary_alw_rec.sudo().unlink()
        return {'type': 'ir.actions.act_window_close'}
