from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import content_disposition, Controller, request, route
import pdb


class EmployeeMarriageGrant(models.Model):
    _name = "marriage.grant"
    _description = "Employee Marriage Grant"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    approved_employee_id = fields.Many2one('hr.employee', string="Approved Employee", tracking=True)
    request_date = fields.Date("Request Date", default=fields.Datetime.now, tracking=True)
    daughter_name = fields.Char('Daughter Name', tracking=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('recommend', 'Recommend'),
                              ('review', 'Review'),
                              ('approved', 'Approved'),
                              ], default='draft', string='Status', tracking=True, index=True)

    age = fields.Char("Age", tracking=True)
    marriage_date = fields.Date("Marriage Date", tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    def action_draft(self):
        self.state = 'draft'

    def action_approved(self):
        self.state = 'approved'
        self.approved_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])

    def action_review(self):
        self.state = 'review'
        group_users = self.env.ref('employee_request.gm_request').users
        if group_users:
            user_id = group_users[0].id

        self.env['mail.activity'].sudo().create({
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get('marriage.grant').id,
            'summary': 'Submitted For Perusal And Approval',
            'note': 'Record Approve Request',
            'activity_type_id': 4,
            'user_id': user_id,
        })
        return True

    def action_recommend(self):
        self.state = 'recommend'
        user_id = False
        group_users = self.env.ref('employee_request.hrm_request').users
        if group_users:
            user_id = group_users[0].id

        self.env['mail.activity'].sudo().create({
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get('marriage.grant').id,
            'summary': 'Submitted For Perusal And Approval',
            'note': 'Record Approve Request',
            'activity_type_id': 4,
            'user_id': user_id and user_id or False,
        })
        return True

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(EmployeeMarriageGrant, self).unlink()

    @api.model
    def create(self, values):
        activity_call = self.env["hr.employee"].search([('job_id', '=', 'General Manager (HR&A)')])
        record = super(EmployeeMarriageGrant, self).create(values)
        if not record.name:
            record.name = self.env['ir.sequence'].next_by_code('marriage.grant')
        for rec in record:
            self.env['mail.activity'].sudo().create({
                'res_id': rec.id,
                'res_model_id': self.env['ir.model']._get('marriage.grant').id,
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
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))

        return request.make_response(report, headers=reporthttpheaders)
