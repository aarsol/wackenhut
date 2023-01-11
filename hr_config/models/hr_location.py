from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class HRLocationType(models.Model):
    _name = 'hr.location.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Location Types'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    remarks = fields.Text('Remarks')

    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Duplicate Records are not Allowed.')]

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(HRLocationType, self).unlink()


class HRLocations(models.Model):
    _name = 'hr.location'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Locations'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    remarks = fields.Text('Remarks')

    @api.constrains('name')
    def duplicate_constrains(self):
        for rec in self:
            already_exist = self.env['hr.location'].search([('name', '=', rec.name),
                                                            ('id', '!=', rec.id)])
            if already_exist:
                raise UserError(_('Duplicate Records are not Allowed.😀😀😀'))

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        link_with_employee = self.env['hr.employee'].search([('location_id', '=', self.id)])
        if link_with_employee:
            raise UserError(_("""You cannot delete the Location that is linked with Some Employee, 
                            Please First remove the link of this location from Employee Profile and then try it."""))
        return super(HRLocations, self).unlink()

