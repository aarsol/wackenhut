from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class EmployeeTravelRequest(models.Model):
    _name = "travel.request"
    _description = "Employee Travel Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "reason"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", tracking=True, index=True)
    request_date = fields.Date(
        "Request Date", default=fields.Datetime.now, tracking=True)
    reason = fields.Text("Reason")
    loc_from = fields.Char("From")
    loc_to = fields.Char("To")
    start_date = fields.Date("Start Date", tracking=True)
    end_date = fields.Date("End Date", tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ('reject', 'Reject'),
                              ], default='draft', string='Status', tracking=True, index=True)
    review_boolean = fields.Boolean('Review ', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=False)

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_recommend(self):
        for rec in self:
            rec.state = 'recommend'

        self.env['mail.activity'].sudo().create({
            'res_id': rec.id,
            'res_model_id': self.env['ir.model']._get('travel.request').id,
            'summary': 'Submitted For Perusal And Approval',
            'note': 'Record Approve Request',
            'activity_type_id': 4,
            'user_id': rec.employee_id.department_id.manager_id.user_id.id,
        })
        return True

    def action_approved(self):
        for rec in self:
            if rec.state=='approved':
                raise UserError('Request Already Approved')
            if rec.state=='reject':
                raise UserError('Request Already Rejected')

            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            if rec.state=='approved':
                raise UserError('Request Already Approved')
            if rec.state=='reject':
                raise UserError('Request Already Rejected')

            rec.state = 'reject'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(
                _('You can delete the Records that are in the Draft State.'))
        return super(EmployeeTravelRequest, self).unlink()

    def create_activity(self):
        self.activity_schedule('employee_request.mail_act_travel_request',
                               user_id=self.employee_id.parent_id.user_id.id)

    # def travel_type_check(self):
    #     if self.employee_id.parent_id.user_id.has_group('employee_request.md_request'):
    #         self.review_boolean = False

    @api.model
    def create(self, values):
        record = super().create(values)
        for rec in record:
            if not rec.employee_id.parent_id:
                record.unlink()
                raise UserError(
                    'This employee has not any Reporting Officer.')
            elif not rec.employee_id.parent_id.user_id:
                record.unlink()
                raise UserError(
                    'No User assigned To Manager')

        if not record.name:
            record.name = self.env['ir.sequence'].next_by_code(
                'travel.request')

        record.create_activity()

        # record.travel_type_check()
        # if not record.review_boolean:
        #     record.state = 'recommend'

        #     self.env['mail.activity'].sudo().create({
        #         'res_id': record.id,
        #         'res_model_id': self.env['ir.model']._get('travel.request').id,
        #         'summary': 'Submitted For Perusal And Approval',
        #         'note': 'Record Approve Request',
        #         'activity_type_id': 4,
        #         'user_id': record.employee_id.parent_id.user_id.id,
        #     })

        # else:
        #     for rec in record:
        #         self.env['mail.activity'].sudo().create({
        #             'res_id': rec.id,
        #             'res_model_id': self.env['ir.model']._get('travel.request').id,
        #             'summary': 'Submitted For Perusal And Approval',
        #             'note': 'Record Approve Request',
        #             'activity_type_id': 4,
        #             'user_id': rec.employee_id.parent_id.user_id.id,
        #         })

        return record
