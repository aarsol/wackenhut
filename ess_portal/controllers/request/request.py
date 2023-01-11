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


class ESSRequestPages(http.Controller):
    @http.route(['/employee/request'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def ess_request(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)

            missed_att_obj = http.request.env['missed.attendance'].sudo()
            missed_att = missed_att_obj.search([('employee_id', '=', employee.id)], order='sequence desc')
            missed_att_progress = missed_att.filtered(lambda s: s.state == 'draft')
            missed_att_history = missed_att.filtered(lambda s: s.state != 'draft')
            
            missed_att_selection_dict = dict(missed_att_obj.fields_get(allfields=['state'])['state']['selection'])
            missed_att_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': missed_att_selection_dict[rec.state],
                'checkin': rec.checkin or False,
                'checkout': rec.checkout or False,
                'checkin_date': self.time_zone_update(rec.checkin_date, True),
                'checkout_date': self.time_zone_update(rec.checkout_date, True),
                'reason': rec.reason,
                'application_date': self.time_zone_update(rec.application_date),
                'table_name': 'missed.attendance',
                'id': rec.id,
            } for rec in missed_att_progress]
            missed_att_history_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': missed_att_selection_dict[rec.state],
                'checkin': rec.checkin or False,
                'checkout': rec.checkout or False,
                'checkin_date': self.time_zone_update(rec.checkin_date),
                'checkout_date': self.time_zone_update(rec.checkout_date),
                'reason': rec.reason,
                'application_date': self.time_zone_update(rec.application_date),
            } for rec in missed_att_history]

            loan_obj = http.request.env['loan.request'].sudo()
            loans = loan_obj.search([('employee_id', '=', employee.id)], order='sequence desc')
            loan_progress = loans.filtered(lambda s: s.state == 'draft')
            loan_history = loans.filtered(lambda s: s.state != 'draft')

            loan_selection_dict = dict(loan_obj.fields_get(allfields=['state'])['state']['selection'])
            loan_progress_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': loan_selection_dict[rec.state],
                'amount': rec.amount,
                'purpose': rec.purpose,
                'apply_date': rec.apply_date,
                'loan_type': dict((rec.fields_get('loan_advance')['loan_advance'])['selection'])[rec.loan_advance],
                'table_name': 'loan.request',
                'id': rec.id,
            } for rec in loan_progress]
            loan_history_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': loan_selection_dict[rec.state],
                'amount': rec.amount,
                'purpose': rec.purpose,
                'apply_date': rec.apply_date,
                'loan_type': dict((rec.fields_get('loan_advance')['loan_advance'])['selection'])[rec.loan_advance],
            } for rec in loan_history]
            
            travel_obj = http.request.env['travel.request'].sudo()
            travels = travel_obj.search([('employee_id', '=', employee.id)])
            travel_progress = travels.filtered(lambda s: s.state == 'draft')
            travel_history = travels.filtered(lambda s: s.state != 'draft')

            travel_selection_dict = dict(travel_obj.fields_get(allfields=['state'])['state']['selection'])
            travel_progress_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': travel_selection_dict[rec.state],
                'loc_from': rec.loc_from,
                'loc_to': rec.loc_to,
                'reason': rec.reason,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'table_name': 'travel.request',
                'id': rec.id,
            } for rec in travel_progress]
            travel_history_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': travel_selection_dict[rec.state],
                'loc_from': rec.loc_from,
                'loc_to': rec.loc_to,
                'reason': rec.reason,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
            } for rec in travel_history]
            
            resign_obj = http.request.env['resign.request'].sudo()
            resigns = resign_obj.search([('employee_id', '=', employee.id)], order='id desc')
            resign_progress = resigns.filtered(lambda s: s.state == 'notice period')
            resign_history = resigns.filtered(lambda s: s.state != 'notice period')
            
            resign_selection_dict = dict(resign_obj.fields_get(allfields=['state'])['state']['selection'])
            resign_progress_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': resign_selection_dict[rec.state],
                'resign_from': rec.resign_from,
                'resign_reason': rec.resign_reason,
                'apply_date': rec.apply_date,
                'table_name': 'resign.request',
                'id': rec.id,
            } for rec in resign_progress]
            resign_history_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': resign_selection_dict[rec.state],
                'resign_from': rec.resign_from,
                'resign_reason': rec.resign_reason,
                'apply_date': rec.apply_date,
            } for rec in resign_history]
            
            values.update({
                'travel_request': travel_progress_dict,
                'travel_history': travel_history_dict,
                'resign_request': resign_progress_dict,
                'resign_history': resign_history_dict,
                'missed_att_request': missed_att_dict,
                'missed_att_history': missed_att_history_dict,
                'loan_request': loan_progress_dict,
                'loan_history': loan_history_dict,
            })
            return http.request.render('ess_portal.ess_portal_request', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('ess_portal.portal_error', values)

    @http.route(['/employee/missed/att/submit'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_miss_att_request(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            checkin = kw.get('checkin')
            checkout = kw.get('checkout')
            reason = kw.get('reason')
            data = {
                'employee_id': employee.id,
                'reason': reason
            }
            if not checkin == 'on' and not checkout == 'on':
                return json.dumps({
                    'message': 'Please choose check In Date Time or check Out Date Time' or False,
                    'color': 'danger',
                    'failed': 'failed'
                })
            if checkin == 'on':
                if len(kw.get('checkin_time')) == 5:
                    checkin_datetime = datetime.strptime(kw.get('checkin_date') + ' ' + kw.get('checkin_time'), '%Y-%m-%d %H:%M')
                else:
                    checkin_datetime = datetime.strptime(kw.get('checkin_date') + ' ' + kw.get('checkin_time'), '%Y-%m-%d %H:%M:%S')
                local_tz = pytz.timezone(request.env.user.partner_id.tz or 'GMT')
                local_dt = local_tz.localize(checkin_datetime, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                data.update({
                    'checkin': True,
                    'checkin_date': datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                })
        
            if checkout == 'on':
                if len(kw.get('checkout_time')) == 5:
                    checkout_datetime = datetime.strptime(kw.get('checkout_date') + ' ' + kw.get('checkout_time'), '%Y-%m-%d %H:%M')
                else:
                    checkout_datetime = datetime.strptime(kw.get('checkout_date') + ' ' + kw.get('checkout_time'), '%Y-%m-%d %H:%M:%S')
                local_tz = pytz.timezone(request.env.user.partner_id.tz or 'GMT')
                local_dt = local_tz.localize(checkout_datetime, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                data.update({
                    'checkout': True,
                    'checkout_date': datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                })
        
            request.env['missed.attendance'].sudo().create(data)
            response = {
                'message': 'Application Submitted Successfully',
                'failed': 'Application Submitted Successfully'
            }
            return json.dumps(response)
    
        except Exception as e:
            return json.dumps({
                'message': str(e),
                'color': 'danger',
                'failed': 'failed'
            })
        
    @http.route(['/employee/advance/payment/submit'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_advance_payment(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)

            # payment_type = kw.get('payment_type')
            # amount = kw.get('amount')
            # purpose = kw.get('purpose')
            data = {
                'employee_id': employee.id,
                'apply_date': datetime.today().date(),
                'loan_advance': kw.get('payment_type')
            }
            if kw.get('purpose') != '':
                data.update({
                    'purpose': kw.get('purpose')
                })

            if not kw.get('amount').isnumeric() or float(kw.get('amount')) <= 0:
                return json.dumps({
                    'failed': 'Please Provide Valid Amount!',
                    'message': 'Please Provide Valid Amount!'
                })
            else:
                data.update({
                    'amount': float(kw.get('amount'))
                })
            rec = request.env['loan.request'].sudo().create(data)
            # record = {
            #     ''
            #
            # }
            data = {
                'status_is': "Success",
                'message': 'Successfully Added'
            }
            data = json.dumps(data)
            return data

        except Exception as e:
            return json.dumps({
                'message': str(e),
                'color': 'danger',
                'failed': 'failed'
            })

    @http.route(['/employee/travel/request/submit'], type='http', auth="user", website=True, method=['POST'],
                csrf=False)
    def ess_travel_request(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)

            # payment_type = kw.get('payment_type')
            # amount = kw.get('amount')
            # purpose = kw.get('purpose')
            data = {
                'employee_id': employee.id,
                'request_date': datetime.today().date(),
                'company_id': values['company'].id,
                'loc_from': kw.get('loc_from'),
                'loc_to':  kw.get('loc_to'),
                'start_date': datetime.strptime(kw.get('start_date'), '%Y-%m-%d') or '',
                'end_date': datetime.strptime(kw.get('end_date'), '%Y-%m-%d') or '',
                'reason': kw.get('reason'),
                'state': 'draft',
            }

            rec = request.env['travel.request'].sudo().create(data)
            # record = {
            #     ''
            #
            # }
            data = {
                'status_is': "Success",
                'message': 'Successfully Requested'
            }
            data = json.dumps(data)
            return data

        except Exception as e:
            return json.dumps({
                'message': str(e),
                'color': 'danger',
                'failed': 'failed'
            })
    
    @http.route(['/employee/resign/request/submit'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_resign_request(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)

            resign_from = kw.get('resign_from')
            resign_from = datetime.strptime(resign_from, '%Y-%m-%d').date()
            reason = kw.get('reason')
            resign_date = datetime.today().date()
            data = {
                'resign_from': resign_from,
                'apply_date': resign_date,
                'resign_reason': reason,
                'employee_id': employee.id,
                'state': 'notice period',
            }

            if employee.state in ('resigned', 'retired', 'terminated'):
                return json.dumps({
                    'message': 'Request Not Valid!' or False,
                    'color': 'danger',
                    'failed': 'failed'
                })

            if request.env['resign.request'].search([('employee_id', '=', employee.id), ('state', '=', 'notice period')]):
                return json.dumps({
                    'message': 'Request Already in pending Stage' or False,
                    'color': 'danger',
                    'failed': 'failed'
                })

            create_request = request.env['resign.request'].sudo().create(data)
            if request.env['hr.employee.payroll.status'].sudo().search([('employee_id', '=', employee.id)]):
                request.env['hr.employee.payroll.status'].sudo().write({
                    'payroll_status': 'stop'
                })
            else:
                request.env['hr.employee.payroll.status'].sudo().create({
                    'employee_id': employee.id,
                    'payroll_status': 'stop',
                    'company_id': employee.company_id and employee.company_id.id or False,
                })
            employee.payroll_status = 'stop'
            employee_contract = request.env['hr.contract'].sudo().search(
                [('employee_id', '=', employee.id), ('state', '=', 'open')])
            employee_contract.date_end = resign_from
            employee.state = 'notice period'
            data = {
                'failed': "Success",
                'message': 'Successfully Requested'
            }
            data = json.dumps(data)
            return data

        except Exception as e:
            return json.dumps({
                'message': str(e),
                'color': 'danger',
                'failed': 'failed'
            })

    def time_zone_update(self, date, day=False):
        try:
            user_timezone = pytz.timezone(request.env.user.tz or request.env.context.get('tz'))
            if day:
                return pytz.utc.localize(date).astimezone(user_timezone).strftime("%a, %d-%b-%Y %H:%M")
            else:
                return pytz.utc.localize(date).astimezone(user_timezone).strftime("%d-%b-%Y %H:%M")
        except:
            return ''