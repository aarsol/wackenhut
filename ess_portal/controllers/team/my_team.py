import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _, api, http
import pytz


class ESSPaymentPages(http.Controller):
    @http.route(['/employee/organo'], type='http', auth="user", website=True, method=['GET'])
    def ess_organo(self):
        try:
            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("ess_portal.portal_error", values)

            # attendance_rec = http.request.env['hr.attendance'].sudo().search(
            #     [('employee_id', '=', employee.id)], order='check_in asc')
            #
            # attendance_rec = http.request.env['hr.attendance'].sudo().search(
            #     [('employee_id', '=', employee.id)], order='check_in asc')
            #
            # self_hod = http.request.env['hr.department'].sudo().search(
            #     [('manager_id.user_id', '=', request.env.user.id)])
            # if self_hod:
            #     values.update({
            #         'sub_employee_attendance': True,
            #     })
            # # attendance_rec.read_group([], fields=['employee_id'], groupby='employee_id')
            # values.update({
            #     'attendance_rec': list(attendance_rec),
            #
            # })
            return http.request.render('ess_portal.ess_portal_team_organo', values)
        except Exception as e:
            values.update({
                'error_message': e or False
            })
            return http.request.render('ess_portal.portal_error', values)

