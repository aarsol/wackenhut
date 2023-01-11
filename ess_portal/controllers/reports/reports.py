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


class ESSReports(http.Controller):
    @http.route(['/employee/reports'], type='http', auth="public", website=True, method=['GET', 'POST'])
    def ess_profile(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            religion = http.request.env['hr.religion'].sudo().search([])
            departments = []
            dept_employee_ids = http.request.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)])
            if dept_employee_ids:
                departments += dept_employee_ids.mapped('department_id')
            values.update({
                'religion': religion,
                'departments': departments
            })
            return http.request.render('ess_portal.ess_portal_reports', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('ess_portal.portal_error', values)
