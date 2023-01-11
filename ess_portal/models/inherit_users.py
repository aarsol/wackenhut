from odoo import models, fields, api, _
import pdb


class ResUsers(models.Model):
    _inherit = "res.users"

    user_type = fields.Selection([
        ('faculty', 'Faculty'), ('student', 'Student'), ('employee', 'Employee')
    ], 'User Type', default='employee')