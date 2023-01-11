from datetime import datetime, date, timedelta, time
from dateutil.rrule import rrule, DAILY
from pytz import timezone, UTC

from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _
from odoo.osv import expression
from odoo.http import content_disposition, Controller, request, route


class EmployeeCard(models.Model):
    _inherit = "hr.employee"

    def _show_employee_card(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)

        report_sudo = request.env.ref(report_ref).sudo([])

        report = self.env.ref(report_ref)._render_qweb_pdf(model.ids)[0]
        reporthttpheaders = [
            ('Content-Type', 'applicant/pdf' if report_type =='pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        print('========================================================')
        print(model.id)
        print('========================================================')
        if report_type =='pdf' and download:
            if model.id:
                filename = "Card.pdf"
            else:
                filename = "Card.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))

        return request.make_response(report, headers=reporthttpheaders)
    

# class TimeOffRequest(models.Model):
#     _name = 'special.hr.leave'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = 'AARSOL Time Off'
#     _rec_name = 'employee_id'
#
#     name = fields.Char('Name')
#     sequence = fields.Integer('Sequence', default=10)
#     employee_id = fields.Many2one('hr.employee', string="Employee")
#     leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
#     department_id = fields.Many2one('hr.department', string="Department")
#     next_on_duty = fields.Many2one('hr.employee', string="Next On Duty Name")
#     date_from = fields.Date(string='Date From', default=fields.Date.today())
#     date_to = fields.Date(string='Date To', default=fields.Date.today())
#     compensatory_date_from = fields.Date("Compensatory Date From")
#     compensatory_date_to = fields.Date("Compensatory Date To")
#     # leave_ids = fields.One2many('hr.leave', 'leave_id')
#     hod_app = fields.Boolean(default=False)
#     hr_app = fields.Boolean(default=False)
#     pro_app = fields.Boolean(default=False)
#     parent_dept_hod = fields.Boolean(default=False)
#     sub_parent_dept_hod = fields.Boolean(default=False)
#     other = fields.Boolean(string="Other", default=False)
#     sub_type_id = fields.Many2one('hr.leave.type', string="Sub Leave Type")
#     leave_purpose = fields.Char("Purpose of Leave")
#     number_of_days = fields.Float(
#         'Duration (Days)', compute='_compute_number_of_days')
#     state = fields.Selection(
#         selection=[('draft', 'Draft'), ('confirm', 'To Approved'),
#                    ('approve', 'Approved'), ('reject', 'Reject'), ],
#         string='State', default='draft', tracking=True, index=True)
#     emp_approved = fields.Many2many('hr.employee')
#     emp_approval = fields.Many2one('hr.employee', )
#     emp_approval_department = fields.Many2one('hr.department')
#     upload_documents = fields.Binary('Attachment')
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)
#
#     """
#     This compute method calculate number of days.....
#     """
#
#     @api.depends('date_from', 'date_to')
#     def _compute_number_of_days(self):
#         for rec in self:
#             if rec.date_from and rec.date_to:
#                 rec.number_of_days = (rec.date_to - rec.date_from).days + 1
