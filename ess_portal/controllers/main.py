from odoo import http
from odoo.http import request
from datetime import datetime, time
from odoo import fields
from dateutil.relativedelta import relativedelta
import pdb


def prepare_portal_values(request):
    company = request.env.user.company_id
    partner = request.env.user.partner_id
    user = request.env.user
    employee = http.request.env['hr.employee'].sudo().search([('user_partner_id', '=', partner.id)])

    portal_user = user.has_group('base.group_portal')
    if not employee or not portal_user and (not portal_user and not user.has_group('ess_portal.group_ess_portal_user')):
        values = {
            'error_message': 'Unauthorized Access',
        }
        return values, False, False

    employee_leaves = http.request.env['hr.leave.allocation'].sudo().search([('employee_id', '=', employee.id)])
    current_date = datetime.now().strftime('%Y-%m-%d')
    notifications = http.request.env['cms.notification'].sudo().search(
         [('visible_for', '=', 'employee'), ('expiry', '>=', current_date)])

    # Worked Hour Calculation
    total_hours = 0
    total_minutes = 0
    time_value = 5
    check_in = datetime.combine(fields.Date.today() + relativedelta(day=1), time.min)
    check_out = datetime.combine(fields.Date.today() + relativedelta(day=31), time.max)
    att_recs = http.request.env['hr.attendance'].sudo().search([
        ('employee_id', '=', employee.id),
        ('check_in', '>=', check_in + relativedelta(hours=-time_value)),
        ('check_out', '<=', check_out + relativedelta(hours=-time_value))
    ], order='check_in')

    if att_recs:
        for att_rec in att_recs:
            worked_hour_list = str(att_rec.worked_hours).split('.')
            total_hours += float(worked_hour_list[0])
            total_minutes += float(worked_hour_list[1])
        hh = total_minutes // 60
        total_hours += hh

    base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    if base_url[-1] == '/':
        base_url = base_url[:-1]

    if not employee:
        values = {
            'error_message': 'Unauthorized Access',
        }
        return values, False, False
    else:
        values = {
            'employee': employee,
            'company': company or False,
            'partner': partner,
            'name': partner.name,
            'employee_leaves': employee_leaves,
            'attendance': total_hours,  # attendance,
            'notifications': notifications,
            'user': user,
            'back_office': user.has_group('ess_portal.group_ess_portal_user'),
            'base_url': base_url,
        }
    return values, True, employee
