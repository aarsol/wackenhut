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
import base64


class ESSLeavePages(http.Controller):
    @http.route(['/employee/leave'], type='http', auth="public", website=True, method=['GET', 'POST'])
    def ess_leave(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)

            leave_regular = http.request.env['hr.leave.allocation'].sudo().search([('employee_id', '=', employee.id)])
            leave_special = http.request.env['hr.leave.type'].sudo().search([('special_leave', '=', True), ('company_id', '=', values['company'].id)])
            next_on_duty_emp = http.request.env['hr.employee'].sudo().search([('department_id', '=', employee.department_id.id),
                                                                              ('id', '!=', employee.id)])

            leave_obj = http.request.env['hr.leave'].sudo()
            leaves = leave_obj.search([('employee_id', '=', employee.id)])
            leaves_progress = leaves.filtered(lambda s: s.state in ('draft', 'confirm', 'validate1'))
            leaves_history = leaves.filtered(lambda s: s.state in ('cancel', 'refuse', 'validate'))

            special_leave_obj = http.request.env['special.hr.leave'].sudo()
            special_leaves = special_leave_obj.search([('employee_id', '=', employee.id)])
            special_progress = special_leaves.filtered(lambda s: s.state in ('draft', 'confirm'))
            special_history = special_leaves.filtered(lambda s: s.state in ('approve', 'reject'))

            leave_selection_dict = dict(leave_obj.fields_get(allfields=['state'])['state']['selection'])
            leaves_progress_dict = [{
                'leave_name': leave.holiday_status_id.name,
                'state': leave_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from.date(),
                'date_to': leave.date_to.date(),
                'table_name': 'hr.leave',
                'id': leave.id,
            } for leave in leaves_progress]

            leaves_history_dict = [{
                'leave_name': leave.holiday_status_id.name,
                'state': leave_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from.date(),
                'date_to': leave.date_to.date(),
            } for leave in leaves_history]

            special_selection_dict = dict(special_leave_obj.fields_get(allfields=['state'])['state']['selection'])
            special_progress_dict = [{
                'leave_name': leave.leave_type_id.name,
                'state': special_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from,
                'date_to': leave.date_to,
                'table_name': 'special.hr.leave',
                'id': leave.id,
            } for leave in special_progress]

            special_history_dict = [{
                'leave_name': leave.leave_type_id.name,
                'state': special_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from,
                'date_to': leave.date_to,
            } for leave in special_history]

            values.update({
                'leave_regular': leave_regular,
                'leave_special': leave_special,
                'next_on_duty_emp': next_on_duty_emp,
                'leaves_progress': leaves_progress_dict,
                'special_progress': special_progress_dict,
                'leaves_history': leaves_history_dict,
                'special_history': special_history_dict,
            })
            return http.request.render('ess_portal.ess_portal_leave', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('ess_portal.portal_error', values)

    @http.route(['/employee/leave/request/submit'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_leave_req_submit(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            leave = http.request.env['hr.leave'].sudo().search([])

            date_from_weekend_check = datetime.strptime(kw.get('date_from'), '%Y-%m-%d').strftime('%A')
            date_to_weekend_check = datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date().strftime('%A')
            if date_from_weekend_check in ('Saturday', 'Sunday') or date_to_weekend_check in ('Saturday', 'Sunday'):
                return json.dumps({
                    'message': 'Date Applied is holiday please change date to or date from',
                    'color': 'danger',
                    'status': 'failed'
                })
            leave_type_id = http.request.env['hr.leave.type'].sudo().search([('id', '=', int(kw.get('leave_type')))])
            if employee.probation:
                if not leave_type_id.annual_leave:
                    return json.dumps({
                        'message': 'Leave Not Allowed For On Probation Employee',
                        'color': 'danger',
                        'status': 'failed'
                    })
            if employee.employment_nature=='visiting':
                if not leave_type_id.visiting_leave:
                    return json.dumps({
                        'message': 'Leave Not Allowed For On Visiting Employee',
                        'color': 'danger',
                        'status': 'failed'
                    })

            leave_data = {}
            next_duty = kw.get('next_on_duty', '')

            if (leave_type_id.name=='Casual' or leave_type_id.name=='casual') and kw.get('half_leave')=='on':
                half_leave = datetime.strptime(kw.get('date_from'), '%Y-%m-%d').date()
                leave_data.update({
                    'request_date_from': half_leave,
                    'request_unit_half': True,
                    'request_date_from_period': kw.get('half_day_leave_shift')
                })

            if kw.get('half_leave')!='on':
                date_from = datetime.strptime(kw.get('date_from'), '%Y-%m-%d')
                d1 = date_from.date()

                date_to = datetime.strptime(kw.get('date_to'), '%Y-%m-%d')
                d2 = date_to.date()

                if d1 > d2:
                    return json.dumps({
                        'message': 'Date from should be less than Date to',
                        'color': 'danger',
                        'status': 'failed'
                    })

                days = (d2 - d1).days  # + 1
                leave_allocation_remaining = request.env['hr.leave.allocation'].sudo().search([
                    ('holiday_status_id', '=', leave_type_id.id),
                    ('employee_id', '=', employee.id)
                ], order='id desc', limit=1).number_of_days_display

                if leave_allocation_remaining < days and leave_type_id.special_leave==False:
                    return json.dumps({
                        'message': 'Sorry! Applied Leaves Beyond Quota',
                        'color': 'danger',
                        'status': 'failed',
                        'failed': 'failed'
                    })

                # If Special Leave or leave more than 24 days
                if days > 24 or leave_type_id.special_leave==True:
                    special_data = {
                        'leave_purpose': kw.get("leave_purpose"),
                        'leave_type_id': leave_type_id.id,
                        'employee_id': employee.id,
                        'department_id': employee.department_id.id,
                        'next_on_duty': next_duty,
                        'date_from': d2,
                        'date_to': d1,
                    }
                    if kw.get("upload_documents")!='undefined':
                        file = kw.get('upload_documents')
                        file = base64.b64encode(file.read())
                        special_data.update({'upload_documents': file})

                    if kw.get('sub_leave_type')=='Compensatory Days' or kw.get('sub_leave_type')=='Compensatory' or kw.get('sub_leave_type')=='compensatory':
                        special_data.update({'compensatory_date_from': datetime.strptime(kw.get('date_from'), '%Y-%m-%d').date()})
                        special_data.update({'compensatory_date_to': datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date()})

                    request.env['special.hr.leave'].sudo().create(special_data)
                    data = {
                        'message': 'Request Submitted!',
                        'failed': 'Request Submitted!',
                        'status': 'Request Submitted!',
                    }
                    return json.dumps(data)

                leave_data.update({
                    'request_date_to': d2,
                    'request_date_from': d1,
                    'date_from': date_from,
                    'date_to': date_to,
                })

            if kw.get("upload_documents")!='undefined':
                file = kw.get('upload_documents')
                file = base64.b64encode(file.read())
                leave_data.update({'upload_documents': file})

            leave_data.update({
                'holiday_status_id': leave_type_id.id,
                'employee_id': employee.id,
                'state': 'confirm',
                'work_pending': kw.get("work_pending"),
                'leave_purpose': kw.get("leave_purpose"),
                'contact_address': kw.get("contact_address"),
            })
            rec = http.request.env['hr.leave'].sudo().create(leave_data)
            if kw.get('half_leave')!='on':
                rec.request_date_to = d2
            if kw.get('half_leave')=='on':
                rec.request_date_to = half_leave

            data = {
                'message': 'Request Submitted!',
                'failed': 'false',
                'status': 'false'
            }
            return json.dumps(data)

        except Exception as e:
            # leave_check = http.request.env['hr.leave'].sudo().search([
            #     ('employee_id', '=', employee.id),
            #     ('request_date_to', '=', datetime.datetime.strptime(kw.get('date_to'), '%Y-%m-%d').date()),
            #     ('request_date_from', '=', datetime.datetime.strptime(kw.get('date_from'), '%Y-%m-%d').date())
            # ], order='id desc')
            # if leave_check:
            #     leave_check[0].state = 'draft'
            #     leave_check[0].unlink()

            return json.dumps({
                'message': str(e),
                'color': 'danger',
                'failed': 'failed',
                'status': 'failed'
            })
