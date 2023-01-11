from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gratuity_selection_area = fields.Selection([('draft', 'Draft Contracts'),
                                                ('open', 'Running Contract'),
                                                ('both', 'Draft and Running Both')
                                                ], config_parameter='hr_gratuity.gratuity_selection_area', default="open", string="Gratuity Selection Area")
