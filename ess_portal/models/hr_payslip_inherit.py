from datetime import datetime, date, timedelta, time
from dateutil.rrule import rrule, DAILY
from pytz import timezone, UTC

from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _
from odoo.osv import expression
from odoo.http import content_disposition, Controller, request, route


class EmployeePaySlip(models.Model):
    _inherit = "hr.payslip"

    def _show_report_payslip(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)

        report_sudo = request.env.ref(report_ref).sudo([])

        report = self.env.ref(report_ref)._render_qweb_pdf(model.ids)[0]
        reporthttpheaders = [
            ('Content-Type', 'applicant/pdf' if report_type=='pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        print('========================================================')
        print(model.id)
        print('========================================================')
        if report_type=='pdf' and download:
            if model.id:
                filename = "Form.pdf"
            else:
                filename = "Form.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))

        return request.make_response(report, headers=reporthttpheaders)
