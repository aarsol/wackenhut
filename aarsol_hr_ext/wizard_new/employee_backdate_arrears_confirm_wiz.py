from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
import pdb


class EmployeeBackDateArrearsConfirmWiz(models.TransientModel):
    _name = 'employee.backdate.arrears.confirm.wiz'
    _description = 'Employee BackDate Arrears Confirm Wizard'

    def _get_employee_ids(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    bb_arrears_ids = fields.Many2many('hr.employee.backdate.arrears', 'employee_bb_arrears_confirm_wiz_rel', 'wiz_id', 'employee_id', 'Employee(s)', default=_get_employee_ids)

    def action_confirm(self):
        for rec in self:
            if rec.bb_arrears_ids:
                for bb_arrears_id in rec.bb_arrears_ids:
                    bb_arrears_id.action_confirm()
