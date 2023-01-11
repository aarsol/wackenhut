from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class HREmployeePromotionType(models.Model):
    _name = 'hr.employee.promotion.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Promotion Types'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    remarks = fields.Text('Remarks')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Duplicate Records are not Allowed.')]

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        if not self.state=='draft':
            raise UserError(_('You can delete the Records that are in the Draft State.'))
        return super(HREmployeePromotionType, self).unlink()
