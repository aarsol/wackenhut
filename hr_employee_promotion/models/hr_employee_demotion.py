from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError
import datetime


class HREmployeeDemotion(models.Model):
    _name = 'hr.employee.demotion'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Employee Demotion'

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_employee_current_info', store=True)
    job_id = fields.Many2one('hr.job', string='Designation', compute='_employee_current_info', store=True)
    contract_id = fields.Many2one('hr.contract', string="Contract", compute='_employee_current_info', store=True)
    current_salary = fields.Float('Current Salary', compute='_employee_current_info', store=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', compute='_employee_current_info', store=True)
    demotion_date = fields.Date('Demotion Date', default=fields.Date.today(), tracking=True)
    promotion_type = fields.Many2one('hr.employee.promotion.type', string="Demotion Type", tracking=True)

    new_department_id = fields.Many2one('hr.department', string='New Department')
    new_job_id = fields.Many2one('hr.job', string='New Designation')
    new_salary = fields.Float('New Salary')
    new_contract_id = fields.Many2one('hr.contract', string="New Contract")
    new_manager_id = fields.Many2one('hr.employee', string='New Manager')

    is_create_new_contract = fields.Boolean("Create New Contract?", default=False)
    copy_allowances = fields.Boolean("Copy Allowances", default=False)
    copy_deductions = fields.Boolean("Copy Deductions", default=False)

    remarks = fields.Text('Remarks')
    state = fields.Selection([('draft', 'Draft'),
                              ('validate', 'Validate'),
                              ('approve', 'Approved'),
                              ('reject', 'Reject')
                              ], string='Status', default='draft', tracking=True)

    def action_validate(self):
        for rec in self:
            rec.state = 'validate'

    def action_approve(self):
        for rec in self:
            if rec.is_create_new_contract:
                contract_id = rec.contract_id
                if not contract_id:
                    contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], order='id desc', limit=1)

                if contract_id:
                    contract_id.state = 'close'
                    date_end = rec.demotion_date

                    contracts = self.env['hr.contract'].search_count([('employee_id', '=', rec.employee_id.id)])
                    contracts += 1
                    contract_name = str(rec.employee_id.name) + '-' + str(contracts)
                    new_contract_date = rec.demotion_date + datetime.timedelta(days=1)
                    new_contract = contract_id.copy(
                        default={
                            'name': contract_name,
                            'state': 'draft',
                            'date_start': new_contract_date,
                            'date_end': False,
                            'wage': rec.new_salary,
                        }
                    )
                    rec.new_contract_id = new_contract and new_contract.id or False

            rec.employee_id.parent_id = (rec.new_manager_id and rec.new_manager_id.id) or \
                                        (rec.manager_id and rec.manager_id.id) or False
            rec.state = 'approve'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    def action_turn_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(HREmployeeDemotion, self).unlink()

    @api.model
    def create(self, values):
        res = super(HREmployeeDemotion, self).create(values)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('hr.employee.demotion')
        return res

    @api.depends('employee_id')
    def _employee_current_info(self):
        for rec in self:
            if rec.employee_id:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], order='id desc', limit=1)
                rec.department_id = rec.employee_id.department_id and rec.employee_id.department_id.id or False
                rec.job_id = rec.employee_id.job_id and rec.employee_id.job_id.id or False
                rec.contract_id = contract_id and contract_id.id or False
                rec.current_salary = contract_id and contract_id.gross_salary or 0.0
                rec.manager_id = rec.employee_id.parent_id and rec.employee_id.parent_id.id or False
