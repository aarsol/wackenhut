import pdb
from odoo import api, fields, models, _


class MissedAttendanceReports(models.AbstractModel):
    _name = 'report.employee_request.missed_attendance_report'
    _description = 'Employee Wise Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        employee_ids = data['form']['employee_ids']
        department_ids = data['form']['department_ids']
        dom = [('application_date', '>=', date_from), ('application_date', '<=', date_to)]
        lines = []

        if employee_ids:
            dom.append(('employee_id', 'in', employee_ids))
        if not employee_ids and department_ids:
            employee_list = self.env['hr.employee'].search([('department_id', 'in', department_ids)])
            if employee_list:
                dom.append(('employee_id', 'in', employee_list.ids))

        att_recs = self.env['missed.attendance'].search(dom)
        if att_recs:
            for att_rec in att_recs:
                att_type = ''
                proposed = att_rec.checkin_date if att_rec.checkin else ''
                if att_rec.checkin and att_rec.checkout:
                    att_type = "Check In/Out"
                elif att_rec.checkin:
                    att_type = "Check In"
                elif att_rec.checkout:
                    att_type = "Check Out"

                line = {
                    'employee': att_rec.employee_id.name,
                    'code': att_rec.employee_id.code,
                    'job': att_rec.employee_id.job_id and att_rec.employee_id.job_id.name or False,
                    'proposed': proposed,
                    'machine_datetime': att_rec.attendance_id and att_rec.attendance_id.boi_ids and
                                        att_rec.attendance_id.bio_ids[0].mechine_id.name or '',
                    'difference': 0,
                    'att_type': att_type,
                    'applied_date': att_rec.application_date.strftime('%d-%m-%Y %H:%M:%S'),
                    'status': att_rec.state
                }
                lines.append(line)
                report = self.env['ir.actions.report']._get_report_from_name(
                    'employee_request.missed_attendance_report')
                docargs = {
                    'doc_ids': docids,
                    'docs': self,
                    'doc_model': report.model,
                    'data': data['form'],
                    'lines': lines,
                }
                return docargs
