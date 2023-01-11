from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date, datetime
import pdb

import logging

_logger = logging.getLogger(__name__)

class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    validate_visible = fields.Integer('USER ID', compute='_set_validate_visible')

    def _set_validate_visible(self):
        context = self._context
        user = context.get('uid')
        employee = self.env['hr.employee'].search([('user_id','=',user)])
        if employee.job_title == 'Rector':
            self.validate_visible = True
        else:
            self.validate_visible = False


    def _get_responsible_for_approval(self):
        self.ensure_one()

        responsible = self.env.user

        if self.holiday_type != 'employee':
            return responsible

        if self.validation_type == 'manager' or (self.validation_type == 'both' and self.state == 'confirm'):
            if self.employee_id.leave_manager_id:
                responsible = self.employee_id.leave_manager_id
            elif self.employee_id.parent_id.user_id:
                responsible = self.employee_id.parent_id.user_id
        elif self.validation_type == 'hr' or (self.validation_type == 'both' and self.state == 'validate1'):
            if self.number_of_days >= 5 and self.state == 'validate1':
                employee_id = self.env['hr.employee'].search([('job_title', '=', 'Rector')])
                responsible = employee_id.user_id
            else:
                responsible = self.employee_id.parent_id.user_id

        if self.number_of_days >= 5 and self.state == 'validate1':
            employee_id = self.env['hr.employee'].search([('job_title','=','Rector')])
            responsible = employee_id.user_id

        return responsible
