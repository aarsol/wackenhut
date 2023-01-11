from odoo import http
from odoo.http import request
from datetime import date
import pdb


def prepare_portal_values(request):
	company = request.env.user.company_id
	partner = request.env.user.partner_id
	employee = http.request.env['hr.employee'].sudo().search([('user_partner_id', '=', partner.id)])
	employee_leaves = http.request.env['hr.leave.allocation'].sudo().search([('employee_id', '=', employee.id)])
	attendance_rec = http.request.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id)])
	attendance = 0
	for rec in attendance_rec:
		attendance = attendance+rec.worked_hours
	if not employee:
		values = {
			'error_message' : 'Unauthorized Access',
		}
		return values, False, False
	else:

		values = {
			'employee_info': employee,
			'company': company or False,
			'partner': partner,
			'name': partner.name,
			'employee_leaves':employee_leaves,
			'attendance':attendance,
		}

		# pdb.set_trace()
	return values, True, employee