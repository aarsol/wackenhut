import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _, api, http
import pytz


class ESSNotificationPages(http.Controller):
    @http.route(['/employee/notification'], type='http', auth="user", website=True, method=['GET'])
    def ess_payment(self):
        try:
            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("ess_portal.portal_error", values)

            return http.request.render('ess_portal.ess_portal_notification', values)
        except Exception as e:
            values.update({
                'error_message': e or False
            })
            return http.request.render('ess_portal.portal_error', values)




