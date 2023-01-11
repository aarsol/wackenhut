import json
from datetime import date
import datetime
from .. import main
from odoo import http
from odoo.http import request
import pdb


class EmployeeLeaveRequest(http.Controller):
    @http.route(['/employee/leave/request/status'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_leave(self, **kw):
        try:

            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            leave_recs = http.request.env['hr.leave'].sudo().search([('employee_id', '=', employee.id)])
            values.update({
                'leave_recs': leave_recs,
            })
            # pdb.set_trace()
            return http.request.render('employee_portal.employee_leave_request_status', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

    @http.route(['/employee/leave/request'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_leave_request(self, **kw):
        try:

            values, success, employee = main.prepare_portal_values(request)
            dropdown_values = []
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            leave_recs = http.request.env['hr.leave.allocation'].sudo().search([('employee_id', '=', employee.id)])
            for rec in leave_recs:
                dropdown_values.append(rec.holiday_status_id.name)

            # pdb.set_trace()
            values.update({
                'dropdown_values': dropdown_values,
            })
            return http.request.render('employee_portal.employee_leave_request', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

    @http.route(['/employee/leave/request/save'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def employee_leave_request_save(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            leave_type_id = http.request.env['hr.leave.type'].sudo().search([('name', '=', kw.get('leave_type'))])
            # leave_check = http.request.env['hr.leave'].sudo().search([('name', '=', kw.get('leave_type')), (
            #     'request_date_to', '=', datetime.datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date()), (
            #                                                                     'request_date_from', '=',
            #                                                                     datetime.datetime.strptime(
            #                                                                         kw.get('date_from'),
            #                                                                         '%Y-%m-%d').date())])
            d1 = datetime.datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date()
            d2 = datetime.datetime.strptime(kw.get('date_from'), '%Y-%m-%d').date()
            date_difference = d1 - d2
            emp_data = {
                'holiday_status_id': leave_type_id.id,
                'request_date_to': datetime.datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date(),
                'request_date_from': datetime.datetime.strptime(kw.get('date_from'), '%Y-%m-%d').date(),
                'date_to': datetime.datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date(),
                'date_from': datetime.datetime.strptime(kw.get('date_from'), '%Y-%m-%d').date(),
                'number_of_days': date_difference.days,
                'employee_id': employee.id,
                'state': 'confirm'
            }

            rec = http.request.env['hr.leave'].sudo().create(emp_data)
            data = {
                'status_is': 'Success',
                }
            data = json.dumps(data)
            return data
        except Exception as e:
            leave_check = http.request.env['hr.leave'].sudo().search([('employee_id', '=', employee.id), (
                    'request_date_to', '=', datetime.datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date()), (
                                                                                    'request_date_from', '=',
                                                                                    datetime.datetime.strptime(
                                                                                        kw.get('date_from'),
                                                                                        '%Y-%m-%d').date())], order='id desc')
            leave_check[0].state = 'draft'
            leave_check[0].unlink()
            # pdb.set_trace()
            data = {
                'status_is': 'Error',
                'error_message': e.args[0] or False
            }

            data = json.dumps(data)
            return data
