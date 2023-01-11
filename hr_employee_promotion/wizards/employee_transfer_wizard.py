from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import pdb


class HREmployeeTransferWizard(models.TransientModel):
    _name = 'hr.employee.transfer.wizard'
    _description = 'Employee Transfer Wizard'

    @api.model
    def _get_employee_id(self):
        emp_id = self.env['hr.employee'].browse(self._context.get('active_id', False))
        return emp_id and emp_id.id or False

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=_get_employee_id)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    job_id = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id')
    manager_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id')
    transfer_date = fields.Date('Transfer Date', default=fields.Date.today())
    transfer_type = fields.Many2one('hr.employee.transfer.type', string="Transfer Type")

    contract_id = fields.Many2one('hr.contract', string="Contract", compute='_employee_current_info', store=True)
    current_salary = fields.Float('Current Salary', compute='_employee_current_info', store=True)

    new_department_id = fields.Many2one('hr.department', string='New Department')
    new_job_id = fields.Many2one('hr.job', string='New Designation')
    new_salary = fields.Float('New Salary')
    new_manager_id = fields.Many2one('hr.employee', string='New Manager')

    is_create_new_contract = fields.Boolean("Create New Contract?", default=False)
    copy_allowances = fields.Boolean("Copy Allowances?", default=False)
    copy_deductions = fields.Boolean("Copy Deductions?", default=False)
    remarks = fields.Text('Remarks')

    @api.depends('employee_id')
    def _employee_current_info(self):
        for rec in self:
            if rec.employee_id:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], order='id desc', limit=1)
                rec.contract_id = contract_id and contract_id.id or False
                rec.current_salary = contract_id and contract_id.gross_salary or 0.0

    def action_transfer_employee(self):
        for rec in self:
            last_salary_slip = self.env['hr.payslip'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', '=', 'done')
                                                              ], order='id desc', limit=1)
            if last_salary_slip:
                slip_date = last_salary_slip.date_to
                if rec.transfer_date < slip_date:
                    raise ValidationError(_('Transfer Date should be Before the Last Salary Date.'))
            res = {
                'employee_id': rec.employee_id.id,
                'department_id': rec.department_id and rec.department_id.id or False,
                'job_id': rec.job_id and rec.job_id.id or False,
                'manager_id': rec.manager_id and rec.manager_id.id or False,
                'contract_id': rec.contract_id and rec.contract_id.id or False,
                'transfer_date': rec.transfer_date,
                'transfer_type': rec.transfer_type and rec.transfer_type.id or False,
                'current_salary': rec.current_salary,
                'new_department_id': rec.new_department_id and rec.new_department_id.id or False,
                'new_job_id': rec.new_job_id and rec.new_job_id.id or False,
                'new_salary': rec.new_salary,
                'new_manager_id': rec.new_manager_id and rec.new_manager_id.id or False,
                'is_create_new_contract': rec.is_create_new_contract,
                'copy_allowances': rec.copy_allowances,
                'copy_deductions': rec.copy_deductions,
                'remarks': rec.remarks,
                'state': 'draft',
            }
            transfer_rec = self.env['hr.employee.transfer'].create(res)

            if transfer_rec:
                transfer_list = transfer_rec.mapped('id')
                form_view = self.env.ref('hr_employee_promotion.view_hr_employee_transfer_form')
                tree_view = self.env.ref('hr_employee_promotion.view_hr_employee_transfer_tree')
                return {
                    'domain': [('id', 'in', transfer_list)],
                    'name': _('Employee Transfer'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'hr.employee.transfer',
                    'view_id': False,
                    'views': [
                        (tree_view and tree_view.id or False, 'tree'),
                        (form_view and form_view.id or False, 'form'),
                    ],
                    'type': 'ir.actions.act_window'
                }
            else:
                return {'type': 'ir.actions.act_window_close'}
