from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class HRProvince(models.Model):
    _name = 'hr.province'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Provinces'

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
        return super(HRProvince, self).unlink()


class HRTransportArea(models.Model):
    _name = 'hr.transport.area'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Transport Areas'

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
        return super(HRTransportArea, self).unlink()


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    location_type_id = fields.Many2one('hr.location.type', 'Location Type')
    province_id = fields.Many2one('hr.province', 'Province')
