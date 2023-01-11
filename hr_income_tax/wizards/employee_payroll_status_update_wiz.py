from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import math
import numpy as np
import numpy_financial as npf
import pdb


class EmployeePayrollStatusUpdateWiz(models.TransientModel):
    _inherit = 'employee.payroll.status.update.wiz'

    def action_update_payroll_status(self):
        for rec in self:
            for employee_id in rec.employee_ids:
                result = super().action_update_payroll_status()
                if rec.payroll_status=='start':
                    tax_slab_id = int(self.env['ir.config_parameter'].sudo().get_param('hr_income_tax.current_tax_slab'))
                    if tax_slab_id:
                        tax_slab_id = self.env['hr.income.tax'].search([('id', '=', tax_slab_id)])
                    if not tax_slab_id:
                        raise UserError(_("Please Configure the Tax Slab for this Financial Year"))
                    if tax_slab_id:
                        stop_request_id = self.env['hr.employee.payroll.status'].search([('employee_id', '=', employee_id.id),
                                                                                         ('payroll_status', '=', 'stop'),
                                                                                         ], order='id desc', limit=1)
                        if not stop_request_id:
                            raise UserError(_('For this Employee its Salary Stop request is not found. \nFor Loan Reschedule its Stop request is necessary'))

                        employee_tax_rec = self.env['hr.employee.income.tax'].search([('employee_id', '=', employee_id.id), ('tax_id', '=', tax_slab_id.id)])
                        if employee_tax_rec:
                            pause_months = ((rec.date.year - stop_request_id.date.year) * 12) + (rec.date.month - stop_request_id.date.month)
                            last_paid_entry = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', employee_tax_rec.id),
                                                                                              ('state', '=', 'Deducted')
                                                                                              ], order='id desc', limit=1)
                            if last_paid_entry:
                                remaining_installments = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', employee_tax_rec.id),
                                                                                                         ('state', '=', 'Deducted'),
                                                                                                         ('id', '>', last_paid_entry.id)
                                                                                                         ], order='id asc')
                            if not last_paid_entry:
                                remaining_installments = self.env['hr.employee.income.tax.line'].search([('employee_tax_id', '=', employee_tax_rec.id),
                                                                                                         ('state', '=', 'Deducted'),
                                                                                                         ], order='id asc')
                                for remaining_installment in remaining_installments:
                                    # To Be Check that if it is at the last of FY then should we delete the tax lines
                                    new_date = remaining_installment.date + relativedelta(months=pause_months)
                                    if new_date < tax_slab_id.date_to:
                                        remaining_installment.date = new_date
                                        remaining_installment.month = new_date.strftime('%B-%Y')
