from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class MissedAttendanceRepWiz(models.TransientModel):
    _name = 'missed.attendance.rep.wiz'
    _description = 'Missed Attendance Report Wizard'

    date_from = fields.Date('From Date', default=fields.Date.today() + relativedelta(day=1))
    date_to = fields.Date('To Date', default=fields.Date.today())
    employee_ids = fields.Many2many("hr.employee", 'missed_attendance_rep_employee_rel', 'wizard_id', 'employee_id', 'Employee(s)')
    department_ids = fields.Many2many("hr.department", 'missed_attendance_rep_department_rel', 'wizard_id', 'department_id', 'Departments')

    def print_report(self):
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'missed.attendance.rep.wiz',
            'form': data
        }
        return self.env.ref("employee_request.action_missed_attendance_report").with_context(landscape=True).report_action(self, data=datas)
