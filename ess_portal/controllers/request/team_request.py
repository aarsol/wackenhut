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
    @http.route(['/employee/team/request'], type='http', auth="user", website=True, method=['GET'])
    def ess_team_request(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            c_user = request.env.user.id

            missed_obj = http.request.env['missed.attendance'].sudo()
            missed_att = missed_obj.search([('employee_id.parent_id.user_id.id', '=', c_user)], order='id desc')
            missed_att_progress = missed_att.filtered(lambda s: s.state == 'draft')
            missed_att_history = missed_att.filtered(lambda s: s.state != 'draft')

            missed_att_selection_dict = dict(missed_obj.fields_get(allfields=['state'])['state']['selection'])
            missed_att_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': missed_att_selection_dict[rec.state],
                'checkin': rec.checkin or False,
                'checkout': rec.checkout or False,
                'checkin_date': self.time_zone_update(rec.checkin_date,True),
                'checkout_date': self.time_zone_update(rec.checkout_date,True),
                'reason': rec.reason,
                'application_date': self.time_zone_update(rec.application_date),
                'table_name': 'missed.attendance',
                'table_name2': 'missed_attendance',
                'id': rec.id,
            } for rec in missed_att_progress]
            missed_att_history_dict = [{
                'name': rec.name,
                'employee_name': rec.employee_id.name,
                'employee_job_name': rec.employee_id.job_id.name,
                'state': missed_att_selection_dict[rec.state],
                'checkin_date': self.time_zone_update(rec.checkin_date),
                'checkout_date': self.time_zone_update(rec.checkout_date),
                'reason': rec.reason,
                'application_date': self.time_zone_update(rec.application_date),
            } for rec in missed_att_history]
            
            leave_obj = http.request.env['hr.leave'].sudo()
            leaves = leave_obj.search([('employee_id.parent_id.user_id.id', '=', c_user)], order='id desc')
            leave_progress = leaves.filtered(lambda s: s.state in ('draft', 'confirm', 'validate1'))
            leave_history = leaves.filtered(lambda s: s.state in ('cancel', 'refuse', 'validate'))

            leave_selection_dict = dict(leave_obj.fields_get(allfields=['state'])['state']['selection'])
            leave_progress_dict = [{
                'leave_name': leave.holiday_status_id.name,
                'employee_name': leave.employee_id.name,
                'employee_job_name': leave.employee_id.job_id.name,
                'state': leave_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'next_on_duty': leave.next_on_duty.name,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from.date(),
                'date_to': leave.date_to.date(),
                'table_name': 'hr.leave',
                'table_name2': 'hr_leave',
                'id': leave.id,
            } for leave in leave_progress]
            leave_history_dict = [{
                'leave_name': leave.holiday_status_id.name,
                'employee_name': leave.employee_id.name,
                'employee_job_name': leave.employee_id.job_id.name,
                'state': leave_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'next_on_duty': leave.next_on_duty.name,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from.date(),
                'date_to': leave.date_to.date(),
            } for leave in leave_history]
            
            
            special_leave_obj = http.request.env['special.hr.leave'].sudo()
            special_leaves = special_leave_obj.search([('emp_approval.user_id.id', '=', c_user)], order='id desc')
            special_progress = special_leaves.filtered(lambda s: s.state in ('draft', 'confirm'))
            special_history = special_leaves.filtered(lambda s: s.state in ('approve', 'reject'))

            special_selection_dict = dict(special_leave_obj.fields_get(allfields=['state'])['state']['selection'])
            special_progress_dict = [{
                'leave_name': leave.leave_type_id.name,
                'employee_name': leave.employee_id.name,
                'employee_job_name': leave.employee_id.job_id.name,
                'state': special_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'next_on_duty': leave.next_on_duty.name,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from,
                'date_to': leave.date_to,
                'table_name': 'special.hr.leave',
                'table_name2': 'special_hr_leave',
                'id': leave.id,
            } for leave in special_progress]
            special_history_dict = [{
                'leave_name': leave.leave_type_id.name,
                'employee_name': leave.employee_id.name,
                'employee_job_name': leave.employee_id.job_id.name,
                'state': special_selection_dict[leave.state],
                'number_of_days': leave.number_of_days,
                'next_on_duty': leave.next_on_duty.name,
                'leave_purpose': leave.leave_purpose,
                'date_from': leave.date_from,
                'date_to': leave.date_to,
            } for leave in special_history]
            
            resign_obj = http.request.env['resign.request'].sudo()
            resigns = resign_obj.search([('emp_approval.user_id.id', '=', c_user)], order='id desc')
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
                'table_name2': 'resign_request',
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
            
            loan_obj = http.request.env['loan.request'].sudo()
            loans = loan_obj.search([('emp_approval.user_id.id', '=', c_user)])
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
                'table_name2': 'loan_request',
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
            travels = travel_obj.search([('employee_id.parent_id.user_id.id', '=', c_user)], order='id desc')
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
                'table_name2': 'travel_request',
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
            
            values.update({
                'leave_progress': leave_progress_dict,
                'special_progress': special_progress_dict,
                'resign_progress': resign_progress_dict,
                'loan_progress': loan_progress_dict,
                'travel_progress': travel_progress_dict,
                
                'leave_history': leave_history_dict,
                'special_history': special_history_dict,
                'resign_history': resign_history_dict,
                'loan_history': loan_history_dict,
                'travel_history': travel_history_dict,
                
                'missed_att_progress': missed_att_dict,
                'missed_att_history': missed_att_history_dict,
            })
            return http.request.render('ess_portal.ess_portal_team_request', values)
        except Exception as e:
            return json.dumps({
                'message': str(e),
                'color': 'danger',
                'failed': 'failed'
            })

    @http.route(['/employee/team/request/approve'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_team_request_approve(self, **kw):
        values, success, employee = main.prepare_portal_values(request)
        try:
            # geting hr user
            hr = request.env['hr.employee'].sudo().search(
                ['&', ('department_id', '=', 'Human Resource Department'), ('job_id', '=', 'Head of HR')]).user_id.id
            # geting prorector user
            prorector = request.env['hr.employee'].sudo().search(
                [('job_id', '=', 'Prorector')]).user_id.id
            # geting finance officer
            finance = request.env['hr.employee'].sudo().search(
                ['&', ('department_id', '=', 'Accounts office'), ('job_id', '=', 'Treasurer')]).user_id.id
            # geting approving request id of
            request_id = kw.get('rec_id')
            # geting request model
            pending_request_model = kw.get('model_name')

            # Leave request apprpovel
            if pending_request_model == 'hr.leave':
                request_leave = request.env['hr.leave'].sudo().search(
                    [('id', '=', int(request_id))])
                if request_leave.state == 'confirm':
                    if request_leave.employee_id.parent_id.user_id.id == request.env.user.id:
                        request_leave.action_approve()
                        return json.dumps({
                            'message': 'Request Approved!',
                            'failed': 'False!',
                            'status': 'true!',
                            'request_id': kw.get('rec_id'),
                            'pending_request_model': kw.get('model_name').replace(".", "_" ),
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                elif request_leave.state == 'validate1':
                    if request.env.user.id == hr:
                        request_leave.action_validate()
                        return json.dumps({
                            'message': 'Request Approved!',
                            'failed': 'False!',
                            'status': 'true!',
                            'request_id': kw.get('rec_id'),
                            'pending_request_model': kw.get('model_name').replace(".", "_" ),
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                else:
                    return json.dumps({
                        'message': 'Athorization Failed!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Travel Request
            if pending_request_model == 'travel.request':
                request_travel = request.env['travel.request'].sudo().search(
                    [('id', '=', int(request_id))])
                request_travel.action_approved()
                return json.dumps({
                    'message': 'Request Approved!',
                    'failed': 'False!',
                    'status': 'true!',
                    'request_id': kw.get('rec_id'),
                    'pending_request_model': kw.get('model_name').replace(".", "_" ),
                })

            # Special Leave Request Approval
            if pending_request_model == 'special.hr.leave':
                try:
                    # special leave request approval
                    special_leave_request = request.env['special.hr.leave'].sudo().search(
                        [('id', '=', int(request_id))])
                    current_user = request.env.user.id
                    special_leave_request_user = special_leave_request.emp_approval.user_id.id
                    if current_user == special_leave_request_user:
                        special_leave_request.approve_request()
                        return json.dumps({
                            'message': 'Request Approved!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                except Exception as e:
                    return json.dumps({
                        'message': str(e),
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Resign Request Approvel
            if pending_request_model == 'resign.request':
                try:

                    resign_request = request.env['resign.request'].sudo().search(
                        [('id', '=', int(request_id))])

                    request_resign_from = resign_request.resign_from

                    current_user = request.env.user.id

                    if kw.get('resign_date') is not None:
                        resign_from_new = datetime.strptime(
                            kw.get('resign_date'), '%Y-%m-%d').date()
                        if request.env.user.id == hr:
                            try:
                                resign_from_new = datetime.strptime(
                                    kw.get('resign_date'), '%Y-%m-%d').date()

                                if type(resign_from_new) == date:
                                    resign_request.resign_from = resign_from_new
                            except:
                                resign_request.resign_from = request_resign_from

                    resign_request_user = resign_request.emp_approval.user_id.id
                    if current_user == resign_request_user:
                        resign_request.approve_request()
                        return json.dumps({
                            'message': 'Request Approved!',
                            'failed': 'False!',
                            'status': 'true!',
                            'request_id': kw.get('rec_id'),
                            'pending_request_model': kw.get('model_name').replace(".", "_" ),
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                except Exception as e:
                    return json.dumps({
                        'message': str(e),
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Loan Request Approve
            if pending_request_model == 'loan.request':
                try:
                    loan_request = request.env['loan.request'].sudo().search(
                        [('id', '=', int(request_id))])
                    current_user = request.env.user.id
                    loan_request_user = loan_request.emp_approval.user_id.id
                    if current_user == loan_request_user:
                        loan_request.approve_request()
                        return json.dumps({
                            'message': 'Request Approved!',
                            'failed': 'False!',
                            'status': 'true!',
                            'request_id': kw.get('rec_id'),
                            'pending_request_model': kw.get('model_name').replace(".", "_" ),
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                except Exception as e:
                    return json.dumps({
                        'message': str(e),
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Missed Attendance Request Approve
            if pending_request_model == 'missed.attendance':
                missed_attendance_request = request.env['missed.attendance'].sudo().search(
                    [('id', '=', int(request_id))])
                if missed_attendance_request.state == 'draft':
                    if request.env.user.id == missed_attendance_request.employee_id.parent_id.user_id.id:
                        missed_attendance_request.action_approved()
                        return json.dumps({
                            'message': 'Request Approved!',
                            'failed': 'False!',
                            'status': 'true!',
                            'request_id': kw.get('rec_id'),
                            'pending_request_model': kw.get('model_name').replace(".", "_" ),
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                elif missed_attendance_request.state == 'approve':
                    return json.dumps({
                        'message': 'Already approved',
                        'failed': 'failed',
                        'status': 'failed!'
                    })
                else:
                    return json.dumps({
                        'message': 'Already rejected',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

        except Exception as e:
            return json.dumps({
                'message': str(e),
                'failed': 'failed',
                'status': 'failed!'
            })

    @http.route(['/employee/team/request/reject'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_team_request_reject(self, **kw):
        values, success, employee = main.prepare_portal_values(request)
        try:
            hr = request.env['hr.employee'].sudo().search(
                ['&', ('department_id', '=', 'Human Resource Department'), ('job_id', '=', 'Head of HR')]).user_id.id
            prorector = request.env['hr.employee'].sudo().search(
                [('job_id', '=', 'Prorector')]).user_id.id
            request_id = kw.get('rec_id')
            pending_request_model = kw.get('model_name')

            # Leave Request Reject
            if pending_request_model == 'hr.leave':
                request_leave = request.env['hr.leave'].sudo().search(
                    [('id', '=', int(request_id))])

                if request_leave.state == 'confirm':
                    if request_leave.employee_id.parent_id.user_id.id == request.env.user.id:
                        request_leave.action_refuse()
                        return json.dumps({
                            'message': 'Request Rejected!',
                                       'failed': 'False!',
                                                 'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                elif request_leave.state == 'validate1':
                    if request.env.user.id == hr:
                        request_leave.action_refuse()
                        return json.dumps({
                            'message': 'Request Rejected!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                else:
                    return json.dumps({
                        'message': 'Athorization Failed!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Travel Request
            if pending_request_model == 'travel.request':
                request_travel = request.env['travel.request'].sudo().search(
                    [('id', '=', int(request_id))])
                request_travel.action_reject()
                return json.dumps({
                    'message': 'Request Rejected!',
                    'failed': 'False!',
                    'status': 'true!'
                })

            # Special Leave Request Reject
            if pending_request_model == 'special.hr.leave':
                try:
                    special_leave_request = request.env['special.hr.leave'].sudo().search(
                        [('id', '=', int(request_id))])
                    if special_leave_request.emp_approval.user_id.id == request.env.user.id:
                        special_leave_request.reject_request()
                        return json.dumps({
                            'message': 'Request Rejected!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                except Exception as e:
                    return json.dumps({
                        'message': str(e),
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Resign Request Reject
            if pending_request_model == 'resign.request':
                try:
                    resign_request = request.env['resign.request'].sudo().search(
                        [('id', '=', int(request_id))])
                    if resign_request.emp_approval.user_id.id == request.env.user.id:
                        resign_request.reject_request()
                        return json.dumps({
                            'message': 'Request Rejected!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                except Exception as e:
                    return json.dumps({
                        'message': 'Athorization Failed!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Missed Attendance Request Reject
            if pending_request_model == 'missed.attendance':
                missed_attendance_request = request.env['missed.attendance'].sudo().search(
                    [('id', '=', int(request_id))])
                if missed_attendance_request.state == 'draft':
                    if request.env.user.id == missed_attendance_request.employee_id.parent_id.user_id.id:
                        missed_attendance_request.action_reject()
                        return json.dumps({
                            'message': 'Request Rejected!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Athorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                elif missed_attendance_request.state == 'approve':
                    return json.dumps({
                            'message': 'Already Rejected!',
                        'failed': 'failed',
                    'status': 'failed!'
                })
                else:
                    return json.dumps({
                        'message': 'Already Rejected!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Loan Request Reject
            if pending_request_model == 'loan.request':
                try:
                    loan_request = request.env['loan.request'].sudo().search(
                        [('id', '=', int(request_id))])
                    if loan_request.emp_approval.user_id.id == request.env.user.id:
                        loan_request.reject_request()
                        return json.dumps({
                            'message': 'Request Rejected!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                except Exception as e:
                    return json.dumps({
                        'message': 'Athorization Failed!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

        except Exception as e:
            return json.dumps({
                'message': str(e),
                'failed': 'failed',
                'status': 'failed!'
            })

    @http.route(['/employee/request/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_request_cancel(self, **kw):
        values, success, employee = main.prepare_portal_values(request)
        try:
            request_id = kw.get('rec_id')
            pending_request_model = kw.get('model_name')

            # Missed Attendance Request Reject
            if pending_request_model == 'missed.attendance':
                missed_attendance_request = request.env['missed.attendance'].sudo().search(
                    [('id', '=', int(request_id))])
                if missed_attendance_request.state == 'draft':
                    if request.env.user.id == missed_attendance_request.employee_id.user_id.id:
                        missed_attendance_request.sudo().unlink()
                        return json.dumps({
                            'message': 'Request Cancelled!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Authorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                else:
                    return json.dumps({
                        'message': 'Cannot be Cancelled!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Loan Request Reject
            if pending_request_model == 'loan.request':
                loan_request = request.env['loan.request'].sudo().search(
                    [('id', '=', int(request_id))])
                
                if loan_request.state == 'draft':
                    if loan_request.employee_id.user_id.id == request.env.user.id:
                        loan_request.sudo().unlink()
                        return json.dumps({
                            'message': 'Request Cancelled!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Authorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                else:
                    return json.dumps({
                        'message': 'Cannot be Cancelled!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Travel Request
            if pending_request_model == 'travel.request':
                request_travel = request.env['travel.request'].sudo().search(
                    [('id', '=', int(request_id))])

                if request_travel.state == 'draft':
                    if request_travel.employee_id.user_id.id == request.env.user.id:
                        request_travel.sudo().unlink()
                        return json.dumps({
                            'message': 'Request Canvelled!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Authorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                else:
                    return json.dumps({
                        'message': 'Cannot be Cancelled!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })

            # Resign Request Reject
            if pending_request_model == 'resign.request':
                resign_request = request.env['resign.request'].sudo().search(
                    [('id', '=', int(request_id))])
                # if resign_request.state == 'draft':
                if resign_request.employee_id.user_id.id == request.env.user.id:
                    resign_request.sudo().unlink()
                    return json.dumps({
                        'message': 'Request Cancelled!',
                        'failed': 'False!',
                        'status': 'true!'
                    })
                else:
                    return json.dumps({
                        'message': 'Authorization Failed!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })
                # else:
                #     return json.dumps({
                #         'message': 'Cannot be Cancelled!',
                #         'failed': 'failed',
                #         'status': 'failed!'
                #     })
            
            # Leave Request Reject
            if pending_request_model == 'hr.leave':
                request_leave = request.env['hr.leave'].sudo().search(
                    [('id', '=', int(request_id))])
            
                if request_leave.state == 'confirm':
                    if request_leave.employee_id.user_id.id == request.env.user.id:
                        request_leave.sudo().unlink()
                        return json.dumps({
                            'message': 'Request Cancelled!',
                            'failed': 'False!',
                            'status': 'true!'
                        })
                    else:
                        return json.dumps({
                            'message': 'Authorization Failed!',
                            'failed': 'failed',
                            'status': 'failed!'
                        })
                else:
                    return json.dumps({
                        'message': 'Cannot be Cancelled!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })
        
            # Special Leave Request Reject
            if pending_request_model == 'special.hr.leave':
                special_leave_request = request.env['special.hr.leave'].sudo().search(
                    [('id', '=', int(request_id))])
                if special_leave_request.employee_id.user_id.id == request.env.user.id:
                    special_leave_request.sudo().unlink()
                    return json.dumps({
                        'message': 'Request Cancelled!',
                        'failed': 'False!',
                        'status': 'true!'
                    })
                else:
                    return json.dumps({
                        'message': 'Authorization Failed!',
                        'failed': 'failed',
                        'status': 'failed!'
                    })
        
        except Exception as e:
            return json.dumps({
                'message': str(e),
                'failed': 'failed',
                'status': 'failed!'
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
