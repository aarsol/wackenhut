import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb


class EmployeeProfile(http.Controller):
    @http.route(['/employee/profile'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_profile(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            # if not success:
            #     return request.render("odoocms_web_bootstrap.portal_error", values)
            # attendance_rec = http.request.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id)])
            # data={
            #
            # }
            return http.request.render('employee_portal.employee_profile', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

    @http.route(['/employee/profile/update'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def employee_profile_update(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            emp_data = {
                'name': kw.get('full_name'),
                'work_email': kw.get('email'),
                'mobile_phone': kw.get('mobile'),
            }
            # pdb.set_trace()
            employee.write(emp_data)
            data = {
                'status_is': 'Success',
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                'status_is': 'Error',
                'error_message': e.args[0] or False
            }
            data = json.dumps(data)
            return data