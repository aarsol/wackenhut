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
import calendar


class essDashboard(http.Controller):
    @http.route(['/employee/dashboard'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def ess_dashboard(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("ess_portal.portal_error", values)
            my_team_members = http.request.env['hr.employee'].sudo().search_count([('parent_id', '=', employee.id)])

            myteam_regular_on_leave = request.env['hr.leave'].sudo().search([
                ('employee_id.parent_id.user_id.id', '=', values['user'].id),
                ('state', 'in', ('validate', 'validate1')),
            ], order='id desc').filtered(lambda x: x.date_from.strftime('%Y-%m-%d')==datetime.now().strftime('%Y-%m-%d'))

            myteam_on_leave_special = request.env['special.hr.leave'].sudo().search([
                ('employee_id.parent_id.user_id.id', '=', values['user'].id),
                ('state', '=', 'approve'),
            ], order='id desc').filtered(lambda x: x.date_from.strftime('%Y-%m-%d')==datetime.now().strftime('%Y-%m-%d'))

            team_attendances = http.request.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)])

            late_members = team_attendances.attendance_ids.filtered(lambda x: x.status=='late' and
                                                                              x.check_in.strftime('%Y-%m-%d')==datetime.now().strftime('%Y-%m-%d'))

            special = request.env['special.hr.leave'].sudo().search([('employee_id', '=', employee.id), ('state', 'not in', ('approve', 'reject'))])
            leave = request.env['hr.leave'].sudo().search([('employee_id', '=', employee.id), ('state', 'not in', ('cancel', 'refuse', 'validate1', 'validate'))])
            miss_att = request.env['missed.attendance'].sudo().search([('employee_id', '=', employee.id), ('state', 'not in', ('approve', 'reject'))])
            travel = request.env['travel.request'].sudo().search([('employee_id', '=', employee.id), ('state', 'not in', ('approved', 'reject'))])
            resign = request.env['resign.request'].sudo().search([('employee_id', '=', employee.id), ('state', 'not in', ('approved', 'reject'))])
            loan = request.env['loan.request'].sudo().search([('employee_id', '=', employee.id), ('state', 'not in', ('approved', 'reject'))])
            my_inprogress_app = len(special) + len(leave) + len(miss_att) + len(travel) + len(resign) + len(loan)

            special_team = request.env['special.hr.leave'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', 'not in', ('approve', 'reject'))])
            leave_team = request.env['hr.leave'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', 'not in', ('cancel', 'refuse', 'validate1', 'validate'))])
            miss_att_team = request.env['missed.attendance'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', 'not in', ('approve', 'reject'))])
            travel_team = request.env['travel.request'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', 'not in', ('approved', 'reject'))])
            resign_team = request.env['resign.request'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', 'not in', ('approved', 'reject'))])
            loan_team = request.env['loan.request'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', 'not in', ('approved', 'reject'))])

            special_app_team = request.env['special.hr.leave'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', '=', ('approve'))])
            leave_app_team = request.env['hr.leave'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', 'in', ('validate1', 'validate'))])
            miss_att_app_team = request.env['missed.attendance'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', '=', ('approve'))])
            travel_app_team = request.env['travel.request'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', '=', ('approved'))])
            resign_app_team = request.env['resign.request'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', '=', ('approved'))])
            loan_app_team = request.env['loan.request'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', '=', ('approved'))])

            special_rej_team = request.env['special.hr.leave'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', '=', ('reject'))])
            leave_rej_team = request.env['hr.leave'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', '=', ('refuse'))])
            miss_att_rej_team = request.env['missed.attendance'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', '=', ('reject'))])
            travel_rej_team = request.env['travel.request'].sudo().search(
                [('employee_id.parent_id.user_id.id', '=', values['user'].id), ('state', '=', ('reject'))])
            resign_rej_team = request.env['resign.request'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', '=', ('reject'))])
            loan_rej_team = request.env['loan.request'].sudo().search(
                [('emp_approval.user_id.id', '=', values['user'].id), ('state', '=', ('reject'))])

            team_inprogress_app = len(special_team) + len(leave_team) + len(miss_att_team) + len(travel_team) + len(resign_team) + len(loan_team)
            team_approv_app = len(special_app_team) + len(leave_app_team) + len(miss_att_app_team) + len(travel_app_team) + len(resign_app_team) + len(loan_app_team)
            team_reject_app = len(special_rej_team) + len(leave_rej_team) + len(miss_att_rej_team) + len(travel_rej_team) + len(resign_rej_team) + len(loan_rej_team)

            # ('type', '!=', False)
            attendance_recs = http.request.env['hr.attendance'].sudo().search(
                [('employee_id', '=', employee.id)], order='check_in desc', limit=8)

            attendance_allocation = http.request.env['hr.leave.allocation'].sudo().search([
                ('employee_id', '=', employee.id)
            ]).filtered(lambda x: x.state in ('validate1', 'validate') and
                                  datetime.now().strftime('%Y-%m-%d') >= x.date_from.strftime('%Y-%m-%d') or datetime.strftime('%Y-%m-%d')
                                  and datetime.now().strftime('%Y-%m-%d') <= x.date_to.strftime('%Y-%m-%d') or datetime.strftime('%Y-%m-%d')
                        )

            
            leaves_data = []
            available_in_category = []
            leaves_allocated = 0
            leaves_available = 0
            points_color = ['#91fc5f', '#fc865f', '#3da2a4', '#ff03cd', '#8338ec', '#fc865f', '#6d6875', '#023047', '8d99ae']
            index = 0

            for rec in attendance_allocation:
                leaves_allocated += rec.number_of_days

            for rec in attendance_allocation:
                leaves_available = leaves_available + (rec.number_of_days or 0 - rec.leaves_taken)

                leaves_data.append({
                    'name': rec.holiday_status_id.name + ' Available',
                    'y': rec.number_of_days or 0 - rec.leaves_taken or 0,
                    'color': points_color[index]
                })
                index += 1

            leaves_availed = leaves_allocated - leaves_available

            leaves_data.append({
                'name': 'Leaves Allocated',
                'y': leaves_allocated,
                'color': points_color[index],
                'sliced': False,
                'selected': True,
            })
            index += 1

            if leaves_availed > 0:
                leaves_data.append({
                    'name': 'Leaves Availed',
                    'y': leaves_availed,
                    'color': points_color[index],
                    'sliced': False,
                    'selected': False,
                })

            # current_date = datetime.now().strftime('%Y-%m-%d')
            # user = request.env['res.users'].browse(request.uid)
            # tz = pytz.timezone(user.partner_id.tz) or pytz.utc
            # current_time = pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%H:%M:%S')
            # alert = False
            # # if current_time > '17:00:00':
            # #     timesheet_recs = http.request.env['account.analytic.line'].sudo().search(
            # #         ['&',('employee_id', '=', employee.id),('date','=',current_date), '|', ('task_id.name', '=', 'Meeting'),
            # #          ('task_id.name', '=', 'Training')])
            # #
            # #
            # #     if not timesheet_recs:
            # #         alert = True
            # notifications = http.request.env['employee.notification'].sudo().search(
            #     [('visible_for', '=', 'employee'), ('expiry', '>=', current_date)])
            # leave_types = http.request.env['hr.leave.allocation'].sudo().search([('employee_id', '=', employee.id)])
            #
            # # Departments
            # departments = []
            #

            # if dept_employee_ids:
            #     departments += dept_employee_ids.mapped('department_id')
            # print("THis is the one being called", date.today() == employee.joining_date)
            # is_work_anniversary = date.today().strftime("%d") == employee.joining_date.strftime("%d")
            # is_birthday = date.today().strftime("%d") == employee.birthday.strftime("%d")
            # family_birthdays = []
            # for member in employee.family_ids:
            #     if date.today().strftime("%d") == member.birthday.strftime("%d"):
            #         family_birthdays.append(member)
            # print("These are family birthdays", family_birthdays)
            # attendance_rec = http.request.env['hr.attendance'].sudo().search(
            #     [('employee_id', '=', employee.id), ('check_in', '>=', date.today() - relativedelta(days=7))],
            #     order='check_in asc')
            # # personal_7_day_attendance = http.request.env['hr.attendance'].sudo().search(
            # #     [('employee_id', '=', employee.id),('check_in','>=',date.today()-relativedelta(days=7))], order='check_in asc')


            values.update({
                'my_team_members': my_team_members,
                'myteam_members_on_leave': len(myteam_regular_on_leave) + len(myteam_on_leave_special),
                'late_members': len(late_members),
                'my_inprogress_app': my_inprogress_app,
                'team_inprogress_app': team_inprogress_app,
                'team_approv_app': team_approv_app,
                'team_reject_app': team_reject_app,
                'total_team_app': team_inprogress_app + team_approv_app + team_reject_app,
                'attendances': attendance_recs,
                'attendance_allocation': attendance_allocation,
                'leaves_data': json.dumps(leaves_data),

                # 'notifications': notifications,
                # 'alert': alert,
                # 'leave_types': leave_types,
                # 'departments': departments,
                # 'is_work_anniversary': is_work_anniversary,
                # 'is_birthday': is_birthday,
                # 'family_birthdays': family_birthdays,
                # 'employee': employee,
                # 'attendance_rec': list(attendance_rec)
            })
            return http.request.render('ess_portal.ess_dashboard', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('ess_portal.portal_error', values)
