from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging
import re
import pdb
import sys
import ftplib
import os
import time
import base64
import codecs
from datetime import datetime, date
from odoo.http import request

_logger = logging.getLogger(__name__)


class EmployeeNotification(models.Model):
    _name = 'employee.notification'
    _description = 'Notification'

    def get_default_user(self):
        return self.env.user.id

    name = fields.Char('Title')
    description = fields.Text('Description')
    url = fields.Html('link')
    date = fields.Date('Date', default=datetime.now())
    expiry = fields.Date('Expiry Date', default=date.today() + relativedelta(days=7))
    uploaded_by = fields.Many2one('res.users', 'Uploaded By', default= get_default_user)
    visible_for = fields.Selection([('employee','Employee')], string='Visible For', default='employee')
    # priority = fields.Boolean('Visible Top', default=False)
    # alert = fields.Boolean('alert', default=False)
    # recipient_ids = fields.Many2many('res.users', 'notification_recipient_rel', 'recipient_id', 'user_id', 'Recipient')
    # allow_preview = fields.Boolean('Allow Preview', default=True)