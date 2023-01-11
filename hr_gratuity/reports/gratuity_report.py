from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
import pdb


class GratuityReport(models.AbstractModel):
    _name = 'report.hr_gratuity.gratuity_report'
    _description = 'Gratuity Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        employee_id = self.env['hr.employee'].search([('id', '=', data['form']['employee_id'][0])])
        retired_date = data['form']['retired_date']
        gratuity_type = data['form']['gratuity_type'][0]
        is_death_case = data['form']['is_death_case']
        report = self.env['ir.actions.report']._get_report_from_name('hr_gratuity.gratuity_report')
        res = []
        total_years = 0
        total_amount = 0
        actual_years = 0
        symbol = ''
        symbol2 = ''
        note = ''

        state = self.env['ir.config_parameter'].sudo().get_param('hr_gratuity.gratuity_selection_area') or 'open'

        contract_id = False
        contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id),
                                                      ('state', '=', state)], order='id desc', limit=1)
        if state=='both':
            contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id),
                                                          ('state', 'in', ('draft', 'open'))], order='id desc', limit=1)

        gratuity_recs = self.env['hr.gratuity.config'].search([('type_id', '=', gratuity_type),
                                                               ('date_to', '>=', employee_id.joining_date),
                                                               ('date_from', '<=', retired_date)], order='date_from')
        if not gratuity_recs:
            raise UserError(_("Please First Define the Gratuity Configuration For this Type"))
        first_rec = 1
        last_rec = len(gratuity_recs)

        for gratuity in gratuity_recs:
            rate = gratuity.rate
            if is_death_case:
                rate = gratuity.rate + gratuity.additional_death_rate

            gratuity_date_from = gratuity.date_from
            gratuity_date_to = gratuity.date_to
            if first_rec==1:
                gratuity_date_from = employee_id.joining_date
            if last_rec==first_rec:
                gratuity_date_to = retired_date

            delta = fields.Date.from_string(gratuity_date_to) - fields.Date.from_string(gratuity_date_from)
            dts = delta.days
            years = round(dts / 365, 2)
            amount = round(contract_id.wage * rate * years, 0)

            total_years += years
            total_amount += amount

            res.append({
                'basic_pay': contract_id.wage,
                'date_from': fields.Date.from_string(gratuity_date_from).strftime('%d-%m-%Y'),
                'date_to': fields.Date.from_string(gratuity_date_to).strftime('%d-%m-%Y'),
                'years': years,
                'rate': rate,
                'additional_rate': gratuity.additional_death_rate,
                'amount': amount,
            })
            first_rec += 1

        if gratuity_recs:
            actual_years = total_years
            rounded_years = round(total_years, 0)
            rounded_diff = round(rounded_years - total_years, 2)
            if rounded_years > total_years:
                res[len(res) - 1]['years'] += rounded_diff
                total_years += rounded_diff
                amt = round(contract_id.wage * rate * rounded_diff, 0)
                res[len(res) - 1]['amount'] += amt
                total_amount += amt
                symbol = 'less'
                symbol2 = 'added'
            if rounded_years < total_years:
                res[len(res) - 1]['years'] -= abs(rounded_diff)
                total_years -= abs(rounded_diff)
                amt = round(contract_id.wage * rate * abs(rounded_diff), 0)
                res[len(res) - 1]['amount'] -= amt
                total_amount -= amt
                symbol = 'higher'
                symbol2 = 'subtracted'

            note = "The Period From " + employee_id.joining_date.strftime("%B %d, %Y") + " to " + fields.Date.from_string(retired_date).strftime(("%B %d, %Y")) \
                   + " is " + str(actual_years) + " which is " + symbol + " by " + str(abs(rounded_diff)) + " From HR Order. Where as the service as per HR Order is " \
                   + str(total_years) + " years. Therefore, the difference of " + str(abs(rounded_diff)) + " is " + symbol2 + " in the Period From " \
                   + fields.Date.from_string(gratuity_date_from).strftime('%d-%m-%Y') + " to " + fields.Date.from_string(gratuity_date_to).strftime('%d-%m-%Y') \
                   + " to equalized with HR Order i.e " + str(actual_years) + " + (" + str(rounded_diff) + ") = " + str(total_years) + " years."

        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'employee': employee_id or False,
            'today': fields.Date.today().strftime('%d-%m-%Y'),
            'retired_date': fields.Date.from_string(retired_date).strftime('%d-%m-%Y'),
            'res': res,
            'total_years': round(total_years, 2),
            'total_amount': round(total_amount, 2),
            'note': note,
        }
        return docargs
