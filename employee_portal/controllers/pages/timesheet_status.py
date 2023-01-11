import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb


class EmployeeTimeSheet(http.Controller):
    @http.route(['/employee/timesheet/history'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_timesheet(self, **kw):
        try:


            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)

            project_ids = http.request.env['project.task'].sudo().search([('allow_timesheets','=',True)])

            timesheet_recs = http.request.env['account.analytic.line'].sudo().search([('employee_id', '=', employee.id),('project_id','in',project_ids.ids)])
            values.update({
                'timesheet_recs':timesheet_recs,
            })
            return http.request.render('employee_portal.employee_time_sheet_history', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

    @http.route(['/employee/timesheet/creation'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_timesheet_creation(self, **kw):
        try:

            values, success, employee = main.prepare_portal_values(request)
            dropdown_values_task = []
            dropdown_values_project = []
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            project_recs = http.request.env['project.project'].sudo().search([('allow_timesheets','=',True)])
            task_recs = http.request.env['project.task'].sudo().search([])
            for rec in project_recs:
                dropdown_values_project.append(rec.name)
            for rec in task_recs:
                dropdown_values_task.append({'id': rec.id, 'name': rec.name})
            # pdb.set_trace()
            values.update({
                'dropdown_values_task': task_recs,
                'dropdown_values_project':dropdown_values_project,
            })
            return http.request.render('employee_portal.employee_timesheet_creation', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

    @http.route(['/project/change'], type='http', auth="user", website=True, method=['GET', 'POST'], csrf=False)
    def project_change(self, **kw):
        # pdb.set_trace()
        try:
            current_user = http.request.env.user
            task_data = []
            project_id = kw.get('project_id')
            # pdb.set_trace()
            project = http.request.env['project.project'].sudo().search([('name','=',project_id)])
            task_recs = http.request.env['project.task'].sudo().search([('project_id','=',project.id)])

            for task in task_recs:
                task_data.append({'id': task.id, 'name': task.name})
            record = {
                'status_is': "noerror",
                'tasks': task_data,
            }

        except:
            record = {'status_is': "error"}

        return json.dumps(record)


    @http.route(['/employee/timesheet/save'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def employee_timeaheet_save(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            project_id = http.request.env['project.project'].sudo().search([('name', '=', kw.get('project'))])
            task_id = http.request.env['project.task'].sudo().search([('id', '=', kw.get('task'))])
            timesheet_data = {
                'date': kw.get('sheet_date'),
                'project_id': project_id.id,
                'task_id': task_id.id,
                'name': kw.get('description'),
                'unit_amount': kw.get('duration'),
                'employee_id': employee.id,
            }
            # pdb.set_trace()
            http.request.env['account.analytic.line'].sudo().create(timesheet_data)
            data = {
                'status_is': 'Success',
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                'status_is': 'Error',
                'error_message': e.args[0] or False
            }
            data = json.dumps(data)
            return data

