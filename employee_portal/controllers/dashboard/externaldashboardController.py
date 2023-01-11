import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb
from datetime import datetime, timedelta
from odoo import fields, models, _, api, http
import pytz


class ExternalDashboard(http.Controller):
    @http.route(['/employee/dashboard'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def f_dashboard(self, **kw):
        try:

            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            current_date = datetime.now().strftime('%Y-%m-%d')
            user = request.env['res.users'].browse(request.uid)
            tz = pytz.timezone(user.partner_id.tz) or pytz.utc
            current_time = pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%H:%M:%S')
            alert = False
            # if current_time > '17:00:00':
            #     timesheet_recs = http.request.env['account.analytic.line'].sudo().search(
            #         ['&',('employee_id', '=', employee.id),('date','=',current_date), '|', ('task_id.name', '=', 'Meeting'),
            #          ('task_id.name', '=', 'Training')])
            #     # pdb.set_trace()
            # 
            #     if not timesheet_recs:
            #         alert = True
            notifications = http.request.env['employee.notification'].sudo().search([('visible_for', '=', 'employee'),('expiry','>=',current_date)])
            leave_types = http.request.env['hr.leave.allocation'].sudo().search([('employee_id','=',employee.id)])

            values.update({
                    'notifications': notifications,
                    'alert': alert,
                    'leave_types': leave_types,
            })
            return http.request.render('employee_portal.employee_dashboard', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)