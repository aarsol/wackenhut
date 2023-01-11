from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_module_resource
import base64
import re
from random import choice
from string import digits
import itertools
from werkzeug import url_encode
import pytz
import pdb


class ResUsers(models.Model):
    _inherit = "res.users"

    user_type = fields.Selection([('faculty', 'Faculty'), ('student', 'Student'), ('employee', 'Employee')],
                                 'User Type', default='employee')
