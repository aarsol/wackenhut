import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb


class EmployeeAttendance(http.Controller):
    @http.route(['/employee/attendance'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_attendance(self, **kw):
        try:


            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            attendance_rec = http.request.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id)])
            values.update({
                'attendance_rec':attendance_rec,
            })
            return http.request.render('employee_portal.employee_attendance', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)