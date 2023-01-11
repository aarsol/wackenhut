from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class HRGratuityConfigType(models.Model):
    _name = 'hr.gratuity.config.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'HR Gratuity Types'

    name = fields.Char('Name', tracking=True, required=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class HRGratuity(models.Model):
    _name = 'hr.gratuity.config'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'HR Gratuity Config'

    name = fields.Char('Name', tracking=True, required=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    date_from = fields.Date('From Date', tracking=True, required=True)
    date_to = fields.Date('To Date', tracking=True, required=True)
    rate = fields.Float('Rate', tracking=True)
    additional_death_rate = fields.Float('Additional Death Rate', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    type_id = fields.Many2one('hr.gratuity.config.type', 'Type', tracking=True, index=True)
    remarks = fields.Text('Remarks')

    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Duplicate Records are not Allowed.')]

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
