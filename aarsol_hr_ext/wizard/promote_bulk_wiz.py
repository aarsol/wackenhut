from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pdb


class EmployeeBulkPromotion(models.TransientModel):
    _name = 'hr.employee.bulk.promote'
    _description = 'Employee Stage Change Wizard'

    @api.model
    def _get_garde_change_id(self):
        if self.env.context.get('active_model', False)=='hr.grade.change' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    @api.model
    def _get_type_value(self):
        ret_value = ''
        if self.env.context.get('active_model', False)=='hr.grade.change' and self.env.context.get('active_id', False):
            result = self.env['hr.grade.change'].browse(self.env.context['active_id'])
            ret_value = result.type
        return ret_value

    @api.model
    def _get_promotion_type_value(self):
        ret_value = ''
        if self.env.context.get('active_model', False)=='hr.grade.change' and self.env.context.get('active_id', False):
            result = self.env['hr.grade.change'].browse(self.env.context['active_id'])
            ret_value = result.promotion_type
        return ret_value

    grade_change_id = fields.Many2one('hr.grade.change', 'Grade Change Ref', default=_get_garde_change_id)
    payscale_ids = fields.Many2many('hr.payscale', string='Payscale')
    employee_ids = fields.Many2many('hr.employee', string='Excluded Employee')
    selected_employee_ids = fields.Many2many('hr.employee', 'bulk_promote_include_employee_rel', 'bulk_promote_wiz_id', 'employee_id', 'Employee(s)')
    type = fields.Selection([('increment', 'Increment'),
                             ('promotion', 'Promotion'),
                             ('Demotion', 'Demotion')
                             ], string='Type', default=_get_type_value)
    promotion_type = fields.Selection([('active_promotion', 'Acting Promotion'),
                                       ('regular_promotion', 'Regular Promotion'),
                                       ], default='regular_promotion', string='Promotion Type')

    def action_create_entries(self):
        for rec in self:
            if not rec.type=='increment':
                raise UserError(_('Bulk Option is for Increment only.'))

            if rec.grade_change_id and not rec.grade_change_id.state=='draft':
                raise UserError(_("Select Record Should be in the Draft State."))

            domain = []
            if rec.payscale_ids:
                domain.append(('payscale_id', 'in', rec.payscale_ids.ids))
            if rec.location_type_ids:
                domain.append(('location_type_id', 'in', rec.location_type_ids.ids))
            if rec.employee_ids:
                domain.append()
            if rec.payscale_ids and rec.location_type_ids and rec.employee_ids:
                domain = [('id', 'not in', rec.employee_ids.ids)]
            if rec.selected_employee_ids:
                domain = [('id', 'in', rec.selected_employee_ids.ids)]
            employee_recs = self.env['hr.employee'].search(domain)
            if len(employee_recs)==0:
                raise UserError(_("For Select Domain, no Employee Found, Please Re-Select your Domain and then try it."))

            if employee_recs:
                for employee_rec in employee_recs:
                    already_exist = self.env['hr.grade.change.line'].search([('employee_id', '=', employee_rec.id),
                                                                             ('grade_change_id', '=', rec.grade_change_id.id)])
                    if already_exist:
                        raise UserError(_("Employee %s already exist in the System, Please check it") % employee_rec.name)

                    # new_stage = employee_rec.stage + 1
                    new_stage = 0
                    personal_pay = 0
                    if employee_rec.stage < employee_rec.payscale_id.stages:
                        new_stage = employee_rec.stage + 1
                    else:
                        new_stage = employee_rec.stage
                        personal_pay = employee_rec.personal_pay_count + 1

                    grade_change_values = {
                        'grade_change_id': rec.grade_change_id and rec.grade_change_id.id or False,
                        'employee_id': employee_rec.id,
                        'grade': employee_rec.payscale_id and employee_rec.payscale_id.id or False,
                        'new_grade': employee_rec.payscale_id and employee_rec.payscale_id.id or False,
                        'stage': employee_rec.stage,
                        'new_stage': new_stage,
                        'personal_pay_count': personal_pay,
                    }
                    new_rec = self.env['hr.grade.change.line'].create(grade_change_values)
        return {'type': 'ir.actions.act_window_close'}
