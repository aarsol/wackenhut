import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb


class EmployeePlanning(http.Controller):
    @http.route(['/employee/plannings'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_attendance(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            planning = http.request.env['planning.slot'].sudo().search([('employee_id', '=', employee.id)])
            values.update({
                'planning':planning,
            })
            return http.request.render('employee_portal.employee_planning', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)