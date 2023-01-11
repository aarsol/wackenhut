from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import pdb


class BulkEmployeeBackDateArrearsWiz(models.TransientModel):
    _name = 'bulk.employee.backdate.arrears.wiz'
    _description = 'Bulk Employee BackDate Arrears Wizard'

    def _get_employee_ids(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")
    slip_month = fields.Date('Slip Month')
    date = fields.Date('Entry Date', default=fields.Date.today())
    calculation_type = fields.Selection([('Existing', 'Existing'),
                                         ('New', 'New'),
                                         ], default='New', tracking=True, index=True)
    ttype = fields.Selection([('basic', 'Basic Pay'),
                              ('allowance', 'Allowance'),
                              ('deduction', 'Deduction'),
                              ('other_deduction', 'Other Deduction')
                              ], default='allowance', string="Type")
    allowance_ids = fields.Many2many('hr.salary.allowances', 'bulk_employee_arrears_alw_wiz_rel1', 'wiz_id', 'allowance_id', 'Allowances')
    deduction_ids = fields.Many2many('hr.salary.deductions', 'bulk_employee_arrears_ded_wiz_rel1', 'wiz_id', 'deduction_id', 'Deductions')
    employee_ids = fields.Many2many('hr.employee', 'bulk_employee_arrears_wiz_rel1', 'wiz_id', 'employee_id', 'Employee(s)', default=_get_employee_ids)
    other_deduction_input_id = fields.Many2one('hr.salary.inputs', 'Other Deduction Inputs', tracking=True)

    @api.onchange('ttype')
    def onchange_ttype(self):
        for rec in self:
            if rec.ttype and rec.ttype=='allowance':
                if rec.deduction_ids:
                    rec.write({'deduction_ids': [(5,)]})
            if rec.ttype and rec.ttype=='deduction':
                rec.write({'allowance_ids': [(5,)]})

    def action_generate_entry(self):
        for rec in self:
            ret_recs = self.env['hr.employee.backdate.arrears']
            if rec.employee_ids:
                for employee_id in rec.employee_ids:
                    # if salary is not stopped
                    if not employee_id.payroll_status=='stop':
                        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id),
                                                                      ('state', 'in', ('draft', 'open'))
                                                                      ], order='id desc', limit=1)
                        # If contract Exist then do this
                        if contract_id:
                            # Prepare Data Dictionary
                            dict_values = {
                                'employee_id': employee_id.id,
                                'employee_code': employee_id.code and employee_id.code or '',
                                'department_id': employee_id.department_id and employee_id.department_id.id or False,
                                'job_id': employee_id.job_id and employee_id.job_id.id or False,
                                'contract_id': contract_id and contract_id.id or False,
                                'date_from': rec.date_from,
                                'date_to': rec.date_to,
                                'slip_month': rec.slip_month,
                                'date': rec.date,
                                'ttype': rec.ttype,
                                'allowance_ids': [[6, 0, rec.allowance_ids.ids]] if self.allowance_ids else [],
                                'deduction_ids': [[6, 0, rec.deduction_ids.ids]] if self.deduction_ids else [],
                                'state': 'draft',
                                'calculation_type': rec.calculation_type,
                                'other_deduction_input_id': rec.other_deduction_input_id and rec.other_deduction_input_id.id or False,
                            }
                            new_rec = self.env['hr.employee.backdate.arrears'].create(dict_values)
                            ret_recs += new_rec

            if ret_recs:
                ret_list = ret_recs.mapped('id')
                form_view = self.env.ref('aarsol_hr_ext.view_hr_employee_backdate_arrears_form')
                tree_view = self.env.ref('aarsol_hr_ext.view_hr_employee_backdate_arrears_tree')
                return {
                    'domain': [('id', 'in', ret_list)],
                    'name': _('Employee BackDate Arrears'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'hr.employee.backdate.arrears',
                    'view_id': False,
                    'views': [
                        (tree_view and tree_view.id or False, 'tree'),
                        (form_view and form_view.id or False, 'form'),
                    ],
                    'type': 'ir.actions.act_window'
                }
            else:
                return {'type': 'ir.actions.act_window_close'}
