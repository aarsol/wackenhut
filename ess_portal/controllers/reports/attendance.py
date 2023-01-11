from .. import main
from odoo import http
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.http import content_disposition, Controller, request, route
import pdb


class ESSAttendanceReports(http.Controller):

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)

        report_sudo = request.env.ref(report_ref).sudo()

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report") % report_ref)

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)([model.id], data={'report_type': report_type})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type=='pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type=='pdf' and download:
            filename = "attendance_detail.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)

    @http.route(['/employee/attendance/detail/download/'], type='http', method=['GET'], csrf=False, auth="user", website=True)
    def ess_attendance_detail_download(self, **kw):
        values, success, employee = main.prepare_portal_values(request)
        date_start = fields.Date.from_string(kw.get('date_from'))
        date_stop = fields.Date.from_string(kw.get('date_to'))
        if kw.get('dept_ids', False):
            employee = http.request.env['hr.employee'].sudo().search([('department_id', 'in', [int(kw.get('dept_ids'))])])

        r = request.env['report.aarsol_hr_attendance_ext.emp_att_det_rep']
        pdf, _ = request.env.ref('aarsol_hr_attendance_ext.action_emp_att_det_rep').sudo().with_context(date_start=date_start, date_stop=date_stop, employee=employee)._render_qweb_pdf(r)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/employee/manual/attendance/download/'], type='http', method=['GET'], csrf=False, auth="user", website=True)
    def ess_manual_attendance_download(self, **kw):
        values, success, employee = main.prepare_portal_values(request)
        date_start = fields.Date.from_string(kw.get('date_from'))
        date_stop = fields.Date.from_string(kw.get('date_to'))
        departments = kw.get('dept_ids', False)
        if departments:
            departments = [int(departments)]
        else:
            departments = False

        r = request.env['report.ucp_employee_request.missed_attendance_report']
        pdf, _ = request.env.ref('ucp_employee_request.action_missed_attendance_report').sudo().with_context(date_start=date_start, date_stop=date_stop, employee=employee, departments=departments)._render_qweb_pdf(r)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/employee/attendance/summary/download/'], type='http', method=['GET'], csrf=False, auth="user", website=True)
    def ess_attendance_summary_download(self, **kw):
        values, success, employee = main.prepare_portal_values(request)
        date_start = fields.Date.from_string(kw.get('date_from'))
        date_stop = fields.Date.from_string(kw.get('date_to'))

        if kw.get('dept_ids', False):
            employee = http.request.env['hr.employee'].sudo().search([('department_id', 'in', [int(kw.get('dept_ids'))])])

        departments = kw.get('dept_ids', False)
        if departments:
            departments = [int(departments)]
        else:
            departments = []

        r = request.env['report.aarsol_hr_attendance_ext.emp_att_det_rep']
        pdf, _ = request.env.ref('aarsol_hr_attendance_ext.action_employee_attendance_summary_report').sudo().with_context(date_start=date_start, date_stop=date_stop, employee=employee, departments=departments)._render_qweb_pdf(r)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
