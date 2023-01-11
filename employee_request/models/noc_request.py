from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import content_disposition, Controller, request, route
import pdb


class EmployeeNOCRequest(models.Model):
    _name = "noc.request"
    _description = "Employee NOC Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "reason"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    approved_employee_id = fields.Many2one('hr.employee', string="Approved Employee")
    request_date = fields.Date("Request Date", default=fields.Datetime.now)
    reason = fields.Text("Reason")
    state = fields.Selection([('draft', 'Draft'),
                              ('recommend', 'Recommend'),
                              ('review', 'Review'),
                              ('approved', 'Approved'),
                              ], default='draft', string='Status', tracking=True, index=True)

    noc_type = fields.Selection([('applying_job', 'Noc for Applying Job'),
                                 ('study', 'Noc For Study'),
                                 ('passport', 'Noc for Passport'),
                                 ], string='NOC Request Type', tracking=True)
    job_name = fields.Char("Name of Job")
    organization_name = fields.Char("Name of Organization")
    degree_name = fields.Char("Name of Degree")
    university_name = fields.Char("Name of University/College")
    shift_name = fields.Selection([('morning', 'Morning'),
                                   ('evening', 'Evening'),
                                   ], string='Shift', tracking=True)
    new_passport = fields.Char("New Passport")
    renew = fields.Char("Renew")
    review_boolean = fields.Boolean('Review ', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    def action_draft(self):
        self.state = 'draft'

    def action_review(self):
        self.state = 'review'
        group_users = self.env.ref('employee_request.gm_request').users
        if group_users:
            user_id = group_users[0].id

            self.env['mail.activity'].sudo().create({
                'res_id': self.id,
                'res_model_id': self.env['ir.model']._get('noc.request').id,
                'summary': 'Submitted For Perusal And Approval',
                'note': 'Record Approve Request',
                'activity_type_id': 4,
                'user_id': user_id,
            })
        return True

    def action_recommend(self):
        self.state = 'recommend'
        group_users = self.env.ref('employee_request.hrm_request').users
        if group_users:
            user_id = group_users[0].id

        self.noc_type_check()
        if not self.review_boolean:
            self.state = 'review'
            group_users = self.env.ref('employee_request.md_request').users
            if group_users:
                user_id = group_users[0].id
                self.env['mail.activity'].sudo().create({
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model']._get('noc.request').id,
                    'summary': 'Submitted For Perusal And Approval',
                    'note': 'Record Approve Request',
                    'activity_type_id': 4,
                    'user_id': user_id,
                })
        return True

    def action_approved(self):
        self.state = 'approved'
        self.approved_employee_id = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)])

    def unlink(self):
        if not self.state=='draft':
            raise UserError(
                _('You can delete the Records that are in the Draft State.'))
        return super(EmployeeNOCRequest, self).unlink()

    def noc_type_check(self):
        if self.employee_id.parent_id.user_id.has_group('employee_request.md_request'):
            self.review_boolean = False

    @api.model
    def create(self, values):
        activity_call = self.env["hr.employee"].search([('job_id', '=', 'General Manager (HR&A)')])
        record = super(EmployeeNOCRequest, self).create(values)

        if not record.name:
            record.name = self.env['ir.sequence'].next_by_code('noc.request')
        record.noc_type_check()

        if not record.review_boolean:
            group_users = self.env.ref('employee_request.gm_request').users
            if group_users:
                user_id = group_users[0].id

                self.env['mail.activity'].sudo().create({
                    'res_id': record.id,
                    'res_model_id': self.env['ir.model']._get('noc.request').id,
                    'summary': 'Submitted For Perusal And Approval',
                    'note': 'Record Approve Request',
                    'activity_type_id': 4,
                    'user_id': user_id,
                })
        else:
            for rec in record:
                if not rec.employee_id.parent_id:
                    record.unlink()
                    raise UserError(
                        'This employee has not any Reporting Officer.')
                elif not rec.employee_id.parent_id.user_id:
                    record.unlink()
                    raise UserError(
                        'No User assigned to reporting officer of this employee.')

                else:
                    self.env['mail.activity'].sudo().create({
                        'res_id': rec.id,
                        'res_model_id': self.env['ir.model']._get('noc.request').id,
                        'summary': 'Submitted For Perusal And Approval',
                        'note': 'Record Approve Request',
                        'activity_type_id': 4,
                        'user_id': rec.employee_id.parent_id.user_id.id,
                    })
        return record

    def _show_report_form(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)
        report_sudo = request.env.ref(report_ref).sudo([])
        report = self.env.ref(report_ref)._render_qweb_pdf(model.ids)[0]
        reporthttpheaders = [
            ('Content-Type', 'applicant/pdf' if report_type=='pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        print('========================================================')
        print(model.id)
        print('========================================================')
        if report_type=='pdf' and download:
            if model.id:
                filename = "Form.pdf"
            else:
                filename = "Form.pdf"
            reporthttpheaders.append(
                ('Content-Disposition', content_disposition(filename)))

        return request.make_response(report, headers=reporthttpheaders)
