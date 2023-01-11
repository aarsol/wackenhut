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


class ESSPaymentPages(http.Controller):
    @http.route(['/employee/payment'], type='http', auth="user", website=True, method=['GET'])
    def ess_payment(self):
        try:
            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("ess_portal.portal_error", values)

            payslips = http.request.env['hr.payslip'].sudo().search(
                [('employee_id', '=', employee.id), ('show_on_portal', '=', True)], order="id desc")
            # pay_slips = http.request.env['hr.payslip'].sudo().search(
            #     [('employee_id', '=', employee.id)], order="id desc")

            values.update({
                'payslips': payslips,
            })
            return http.request.render('ess_portal.ess_portal_payment', values)
        except Exception as e:
            values.update({
                'error_message': e or False
            })
            return http.request.render('ess_portal.portal_error', values)

    @http.route(['/employee/pay/slip/download/<int:payslip_id>'], type='http', auth="user", website=True,
                method=['GET', 'POST'])
    def ess_download_pay_slip(self, **kw):
        current_user = http.request.env.user
        values, success, employee = main.prepare_portal_values(request)
        payslip = http.request.env['hr.payslip'].sudo().search([('id', '=', kw.get('payslip_id'))])
        return payslip._show_report_payslip(model=payslip, report_type='pdf',
                                            report_ref='ucp_hr_payroll_reports_ext.action_ucp_payslip_report',
                                            download=True)

