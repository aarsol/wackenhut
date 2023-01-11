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


class ESSProfilePages(http.Controller):
    @http.route(['/employee/profile'], type='http', auth="public", website=True, method=['GET', 'POST'])
    def ess_profile(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            religion = http.request.env['hr.religion'].sudo().search([])
            resume_types = http.request.env['hr.resume.line.type'].sudo().search([])
            resume_lines = [{
                'resume_type': resume_type.name,
                'resume_lines': employee.resume_line_ids.filtered(lambda l: l.line_type_id.id == resume_type.id),
            } for resume_type in resume_types]
            values.update({
                'religion': religion,
                'resume_types': resume_types,
                'resume_lines': resume_lines,
            })
            return http.request.render('ess_portal.ess_portal_profile', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('ess_portal.portal_error', values)

    @http.route(['/employee/family'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def ess_family(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            family_ids = http.request.env['hr.employee.family'].sudo().search([('employee_id','=',employee.id)],order='birthday')
            values.update({
                'family_ids': family_ids
            })
            return http.request.render('ess_portal.ess_portal_family', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('ess_portal.portal_error', values)

    @http.route(['/employee/family/submit'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_family_submit(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)

            employee.family_ids.sudo().create({
                'employee_id': employee.id,
                'name': kw.get('member_name'),
                'relationship': kw.get('member_relationship'),
                'birthday': datetime.strptime(kw.get('member_dob'), '%Y-%m-%d') or '',
                'cnic': kw.get('member_cnic'),
                'phone_no': kw.get('member_contact'),
                'status': kw.get('member_status'),
            })
            family_ids = http.request.env['hr.employee.family'].sudo().search([('employee_id', '=', employee.id)])
            values.update({
                'family_ids': family_ids
            })
            return http.request.render('ess_portal.ess_portal_family', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('ess_portal.portal_error', values)

    @http.route(['/employee/resume/add'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def ess_resume_add(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            data = {
                'employee_id': employee.id,
                'name': kw.get('resume_name'),
                'date_start': kw.get('date_start') and datetime.strptime(kw.get('date_start'), '%Y-%m-%d') or False,
                'date_end': kw.get('date_stop') and datetime.strptime(kw.get('date_stop'), '%Y-%m-%d') or False,
                'line_type_id': int(kw.get('resume_type')),
                'display_type': 'classic',
                'reporting_to': kw.get('reporting_to'),
                'job_position': kw.get('job_position'),
                'degree_level': kw.get('degree_level'),
                'year': kw.get('passing_year'),
                'institute_name': kw.get('institute'),
                'board': kw.get('board'),
                'subjects': kw.get('subjects'),
                'organization': kw.get('organization'),
                'certificate_name': kw.get('certificate'),
            }
            employee.resume_line_ids.sudo().create(data)
            
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
            