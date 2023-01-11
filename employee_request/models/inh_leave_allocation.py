from odoo import models, fields, api, _
import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from odoo.tools import date_utils
from odoo.tools.safe_eval import safe_eval
import re
import pdb
from odoo.http import content_disposition, Controller, request, route
from odoo.exceptions import ValidationError, UserError


class EmployeeAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    # holiday_type = fields.Selection(selection_add=[('nature', 'Employment Nature')])
    # payment_type = fields.Selection(selection_add=[('addvance_payment', 'Advance Rent')])

    holiday_type = fields.Selection([('employee', 'By Employee'),
                                     ('company', 'By Company'),
                                     ('department', 'By Department'),
                                     ('category', 'By Employee Tag'),
                                     ('nature', 'By Employment Nature'),
                                     ],
                                    string='Allocation Mode', readonly=True, required=True, default='employee',
                                    states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                    help="Allow to create requests in batchs:\n- By Employee: for a specific employee"
                                         "\n- By Company: all employees of the specified company"
                                         "\n- By Department: all employees of the specified department"
                                         "\n- By Employee Tag: all employees of the specific employee group category")
    employment_nature = fields.Selection([
        ('regular', 'Regular'),
        ('contract', 'Contract'),
    ], string="Employment Nature")

    def _action_validate_create_childs(self):
        childs = self.env['hr.leave.allocation']
        if self.state=='validate' and self.holiday_type in ['category', 'department', 'company', 'nature']:
            if self.holiday_type=='category':
                employees = self.category_id.employee_ids
            elif self.holiday_type=='department':
                employees = self.department_id.member_ids
            # -----customizations basit
            elif self.holiday_type=='nature':
                if self.employment_nature=='regular':
                    employees = self.env['hr.employee'].search(
                        [('employment_nature', '=', 'regular'),
                         ('gender', '=', 'female')]) if self.holiday_status_id.leaves_type=='maternity' else self.env[
                        'hr.employee'].search(
                        [('employment_nature', '=', 'regular')])
                elif self.employment_nature=='contract':
                    employees = self.env['hr.employee'].search(
                        [('employment_nature', '=', 'contract'),
                         ('gender', '=', 'female')]) if self.holiday_status_id.leaves_type=='maternity' else self.env[
                        'hr.employee'].search(
                        [('employment_nature', '=', 'contract')])
            # ---------------------
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])

            for employee in employees:
                childs += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(self._prepare_holiday_values(employee))
            # TODO is it necessary to interleave the calls?
            childs.action_approve()
            if childs and self.validation_type=='both':
                childs.action_validate()
        return childs


class TimeOffExt(models.Model):
    _inherit = 'hr.leave.type'
    _description = 'Leave Type'

    annual_leave = fields.Boolean(string='Allow in Probation', default=True)
    visiting_leave = fields.Boolean(string='Allow Leave for Visiting Employee')
    special_leave = fields.Boolean(string="Special Leave")


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'
    _description = 'Leave Type'

    leave_purpose = fields.Char("Purpose of Leave")
    contact_address = fields.Char("Contact address during leave")
    work_pending = fields.Text(string="Work Pending to be managed by next on duty")
    next_on_duty = fields.Many2one('hr.employee', string="Next On Duty Name")
    upload_documents = fields.Binary(string="Upload Documents")
    # contract_type = fields.Selection(related="employee_id.employment_nature", store=True)
    # probation = fields.Boolean(related="employee_id.probation", store=True)
    leave_id = fields.Many2one('special.hr.leave')

    @api.model
    def create(self, vals):
        vals = super(HolidaysRequest, self).create(vals)
        # if vals.probation==True and vals.holiday_status_id.annual_leave==False:
        #     raise UserError("Annual leave not allowed during probation period..")

        # elif vals.contract_type=='visiting' and vals.holiday_status_id.visiting_leave==False:
        #     raise UserError("Visiting Employee are not allowed for any kind of leave..")

        return vals

    def _show_report_form(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)
        report_sudo = request.env.ref(report_ref).sudo([])
        report = self.env.ref(report_ref)._render_qweb_pdf(model.ids)[0]
        reporthttpheaders = [
            ('Content-Type', 'applicant/pdf' if report_type=='pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        print('========================================================')
        print(model.id)
        print('========================================================')
        if report_type=='pdf' and download:
            if model.id:
                filename = "Form.pdf"
            else:
                filename = "Form.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))

        return request.make_response(report, headers=reporthttpheaders)
