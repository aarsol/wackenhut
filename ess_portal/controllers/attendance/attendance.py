import json
from .. import main
from odoo.http import request
import pdb
from datetime import datetime, timedelta
from odoo import fields, models, _, api, http


class ESSAttendancePages(http.Controller):
    @http.route(['/employee/attendance'], type='http', auth="public", website=True, method=['GET', 'POST'])
    def ess_attendance(self):
        try:
            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("ess_portal.portal_error", values)

            attendance_rec = http.request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id), ('check_in','!=',False)
            ], order='check_in desc', limit=90)

            self_hod = http.request.env['hr.department'].sudo().search([('manager_id.user_id', '=', request.env.user.id)])
            if self_hod:
                values.update({
                    'sub_employee_attendance': True,
                })
            # attendance_rec.read_group([], fields=['employee_id'], groupby='employee_id')
            values.update({
                'attendance_rec': list(attendance_rec),
            })
            return http.request.render('ess_portal.ess_portal_attendance', values)
        except Exception as e:
            values.update({
                'error_message': e or False
            })
            return http.request.render('ess_portal.portal_error', values)

    @http.route(['/employee/attendance/subordinate'], type='http', auth="public", website=True, method=['GET', 'POST'])
    def ess_attendance_subordinate(self):
        try:
            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("ess_portal.portal_error", values)

            employees = http.request.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)])
            attendances = employees.attendance_ids.filtered(lambda l: l.check_in and l.check_in >= (datetime.now() - timedelta(days=30))) \
                .sorted(key=lambda r: r.id, reverse=True)

            values.update({
                'attendances': attendances,
            })
            return http.request.render('ess_portal.ess_portal_attendance_subordinate', values)
        except Exception as e:

            values.update({
                'error_message': e or False
            })
            return http.request.render('ess_portal.portal_error', values)