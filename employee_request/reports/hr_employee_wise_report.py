import pdb
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta, time
from odoo.tools.safe_eval import safe_eval
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HREmployeeWiseAttendanceReports(models.AbstractModel):
    _name = 'report.employee_request.employee_wise_reportaaa'
    _description = 'Employee Wise Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        employee_id = data['form']['employee'] and data['form']['employee'][0] or False
        department_id = data['form']['department'] and data['form']['department'][0] or False
        employee_rec = self.env['missed.attendance'].search([('employee_id', '=', employee_id)])
        department_rec = self.env['missed.attendance'].search([('employee_id.department_id', '=', department_id)])

        employe_list = []
        user_time_zone = pytz.timezone((self.env.user.tz))
        for dep in department_rec:
            employe_dict = {}
            employe_dict.update({
                'code': dep.employee_id.code,
                'employe_name': dep.employee_id.name,
                'job': dep.employee_id.job_id.name,
                'checkin': dep.checkin,
                'checkout': dep.checkout,
                'applied_date_time': dep.application_date,
                'status': dep.state,
                'checkin_date': None,
                'checkout_date': None,
                'checkin_machine_date': None,
                'checkout_machine_date': None,
                'checkin_date_difference': None,
                'checkout_date_difference': None,
            })
            if dep.checkin_date and dep.checkout_date == False:
                time_zone_manage = pytz.utc.localize(dep.checkin_date, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                    user_time_zone)
                check_in_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                  '%Y-%m-%d %H:%M:%S')
                employe_dict.update({
                    'checkin_date': check_in_date,
                })
                machine_req = self.env['biometric.data'].search(
                    [('attendance_id.employee_id.department_id', '=', department_id), ('state', '=', '0'),
                     ('name', '<', dep.checkin_date.date() + timedelta(days=1)),
                     ('name', '>', dep.checkin_date.date() - timedelta(days=1))], order='name', limit=1).name

                if machine_req:
                    time_zone_manage = pytz.utc.localize(machine_req, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                        user_time_zone)
                    machine_checkin_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                             '%Y-%m-%d %H:%M:%S')
                else:
                    machine_checkin_date = None

                employe_dict.update({
                    'checkin_machine_date': machine_checkin_date,
                })
                if machine_checkin_date != None:

                    if check_in_date > machine_checkin_date:
                        difference_in_date = (check_in_date - machine_checkin_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkin_date_difference': difference_in_date,
                        })

                    elif machine_checkin_date == None:
                        employe_dict.update({
                            'checkin_date_difference': 'None',
                        })
                    else:
                        difference_in_date = (check_in_date - machine_checkin_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkin_date_difference': difference_in_date,
                        })
                        employe_dict.update({
                            'checkin_date_difference': machine_checkin_date - check_in_date,
                        })
                employe_list.append(employe_dict)

            if dep.checkout_date and dep.checkin_date == False:
                time_zone_manage = pytz.utc.localize(dep.checkout_date, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                    user_time_zone)
                check_out_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                   '%Y-%m-%d %H:%M:%S')
                employe_dict.update({
                    'checkout_date': check_out_date,
                })

                machine_req = self.env['biometric.data'].sudo().search(
                    [('attendance_id.employee_id.department_id', '=', department_id), ('state', '=', '1'),
                     ('name', '<', dep.checkout_date.date() + timedelta(days=1)),
                     ('name', '>', dep.checkout_date.date() - timedelta(days=1))], order='id desc', limit=1).name

                if machine_req:
                    time_zone_manage = pytz.utc.localize(machine_req, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                        user_time_zone)
                    machine_checkout_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                              '%Y-%m-%d %H:%M:%S')
                else:
                    machine_checkout_date = None

                employe_dict.update({
                    'checkout_machine_date': machine_checkout_date,
                })
                if machine_checkout_date != None:
                    if check_out_date > machine_checkout_date:
                        difference_in_date = (check_out_date - machine_checkout_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkout_date_difference': difference_in_date,
                        })

                    elif machine_checkout_date == None:
                        employe_dict.update({
                            'checkout_date_difference': 'None',
                        })
                    else:
                        difference_in_date = (check_out_date - machine_checkout_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkout_date_difference': difference_in_date,
                        })
                        employe_dict.update({
                            'checkout_date_difference': machine_checkout_date - check_out_date,
                        })
                employe_list.append(employe_dict)

        for dep in employee_rec:
            employe_dict = {}
            employe_dict.update({
                'code': dep.employee_id.code,
                'employe_name': dep.employee_id.name,
                'job': dep.employee_id.job_id.name,
                'checkin': dep.checkin,
                'checkout': dep.checkout,
                'applied_date_time': dep.application_date,
                'status': dep.state,
                'checkin_date': None,
                'checkout_date': None,
                'checkin_machine_date': None,
                'checkout_machine_date': None,
                'checkin_date_difference': None,
                'checkout_date_difference': None,
            })
            if dep.checkin_date and dep.checkout_date == False:
                time_zone_manage = pytz.utc.localize(dep.checkin_date, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                    user_time_zone)
                check_in_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                  '%Y-%m-%d %H:%M:%S')
                employe_dict.update({
                    'checkin_date': check_in_date,
                })
                machine_req = self.env['biometric.data'].search(
                    [('attendance_id.employee_id', '=', employee_id), ('state', '=', '0'),
                     ('name', '<', dep.checkin_date.date() + timedelta(days=1)),
                     ('name', '>', dep.checkin_date.date() - timedelta(days=1))], order='name', limit=1).name

                if machine_req:
                    time_zone_manage = pytz.utc.localize(machine_req, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                        user_time_zone)
                    machine_checkin_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                             '%Y-%m-%d %H:%M:%S')
                else:
                    machine_checkin_date = None

                employe_dict.update({
                    'checkin_machine_date': machine_checkin_date,
                })
                if machine_checkin_date != None:

                    if check_in_date > machine_checkin_date:
                        difference_in_date = (check_in_date - machine_checkin_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkin_date_difference': difference_in_date,
                        })

                    elif machine_checkin_date == None:
                        employe_dict.update({
                            'checkin_date_difference': 'None',
                        })
                    else:
                        difference_in_date = (check_in_date - machine_checkin_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkin_date_difference': difference_in_date,
                        })
                        employe_dict.update({
                            'checkin_date_difference': machine_checkin_date - check_in_date,
                        })
                employe_list.append(employe_dict)

            if dep.checkout_date and dep.checkin_date == False:
                time_zone_manage = pytz.utc.localize(dep.checkout_date, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                    user_time_zone)
                check_out_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                   '%Y-%m-%d %H:%M:%S')
                employe_dict.update({
                    'checkout_date': check_out_date,
                })

                machine_req = self.env['biometric.data'].sudo().search(
                    [('attendance_id.employee_id', '=', employee_id), ('state', '=', '1'),
                     ('name', '<', dep.checkout_date.date() + timedelta(days=1)),
                     ('name', '>', dep.checkout_date.date() - timedelta(days=1))], order='id desc', limit=1).name

                if machine_req:
                    time_zone_manage = pytz.utc.localize(machine_req, DEFAULT_SERVER_DATETIME_FORMAT).astimezone(
                        user_time_zone)
                    machine_checkout_date = datetime.strptime(datetime.strftime(time_zone_manage, '%Y-%m-%d %H:%M:%S'),
                                                              '%Y-%m-%d %H:%M:%S')
                else:
                    machine_checkout_date = None

                employe_dict.update({
                    'checkout_machine_date': machine_checkout_date,
                })
                if machine_checkout_date != None:
                    if check_out_date > machine_checkout_date:
                        difference_in_date = (check_out_date - machine_checkout_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkout_date_difference': difference_in_date,
                        })

                    elif machine_checkout_date == None:
                        employe_dict.update({
                            'checkout_date_difference': 'None',
                        })
                    else:
                        difference_in_date = (check_out_date - machine_checkout_date).total_seconds()
                        seconds = difference_in_date % (24 * 3600)
                        hour = seconds // 3600
                        seconds %= 3600
                        minutes = seconds // 60
                        seconds %= 60
                        difference_in_date = f"{int(hour)}:{int(minutes)}:{int(seconds)}"

                        employe_dict.update({
                            'checkout_date_difference': difference_in_date,
                        })
                        employe_dict.update({
                            'checkout_date_difference': machine_checkout_date - check_out_date,
                        })
                employe_list.append(employe_dict)

        report = self.env['ir.actions.report']._get_report_from_name(
            'employee_request.employee_wise_reportaaa')
        docargs = {
            'doc_ids': docids,
            'docs': self,
            'doc_model': report.model,
            'data': data['form'],
            'employee': employee_rec or False,
            'machine': machine_req or False,
            'employee_list': employe_list,
        }
        return docargs
