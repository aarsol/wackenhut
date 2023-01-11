import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb
from datetime import datetime, timedelta


import time


class EmployeeNotifications(http.Controller):
    @http.route(['/employee/notifications'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_notification(self, **kw):
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')

            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            notifications = http.request.env['employee.notification'].sudo().search([('visible_for', '=', 'employee'),('expiry','>=',current_date)])
            values.update({
                'notifications':notifications,
            })
            return http.request.render('employee_portal.employee_notifications', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

