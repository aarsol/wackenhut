import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CalcGuarantorGratuityWiz(models.TransientModel):
    _name = 'calc.guarantor.gratuity.wiz'
    _description = 'Guarantor Gratuity Calculation Wizard'

    @api.model
    def _get_guarantor_id(self):
        if self.env.context.get('active_id', False):
            return self.env.context['active_id']

    guarantor_id = fields.Many2one('hr.loan.guarantor', 'Guarantor', default=_get_guarantor_id)
    employee_id = fields.Many2one('hr.employee', 'Employee', related='guarantor_id.employee_id')
    joining_date = fields.Date('Joining Date', related='guarantor_id.employee_id.joining_date')
    guarantee_date = fields.Date('Guarantee Date')
    gratuity_type = fields.Many2one('hr.gratuity.config.type', 'Type')
    is_death_case = fields.Boolean('Is Death Case?', default=False)

    def action_calc_gratuity(self):
        for rec in self:
            if rec.guarantor_id:
                contract_id = False
                total_amount = 0
                total_years = 0
                state = self.env['ir.config_parameter'].sudo().get_param('hr_gratuity.gratuity_selection_area') or 'open'
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', '=', state)
                                                              ], order='id desc', limit=1)
                if state=='both':
                    contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                                  ('state', 'in', ('draft', 'open'))
                                                                  ], order='id desc', limit=1)

                gratuity_recs = self.env['hr.gratuity.config'].search([('type_id', '=', rec.gratuity_type.id),
                                                                       ('date_to', '>=', rec.joining_date),
                                                                       ('date_from', '<=', rec.guarantee_date)
                                                                       ], order='date_from')

                if not gratuity_recs:
                    raise UserError(_("Please First Define the Gratuity Configuration For this Type"))
                first_rec = 1
                last_rec = len(gratuity_recs)

                for gratuity in gratuity_recs:
                    amount = 0
                    rate = gratuity.rate
                    if rec.is_death_case:
                        rate = gratuity.rate + gratuity.additional_death_rate

                    gratuity_date_from = gratuity.date_from
                    gratuity_date_to = gratuity.date_to
                    if first_rec==1:
                        gratuity_date_from = rec.employee_id.joining_date
                    if last_rec==first_rec:
                        gratuity_date_to = rec.guarantee_date

                    delta = fields.Date.from_string(gratuity_date_to) - fields.Date.from_string(gratuity_date_from)
                    dts = delta.days
                    years = round(dts / 365, 2)
                    amount = round(contract_id.wage * rate * years, 0)

                    total_years += years
                    total_amount += amount

                    first_rec += 1

                if gratuity_recs:
                    rounded_years = round(total_years, 0)
                    rounded_diff = round(rounded_years - total_years, 2)
                    if rounded_years > total_years:
                        amt = round(contract_id.wage * rate * rounded_diff, 0)
                        total_amount += amt

                    if rounded_years < total_years:
                        amt = round(contract_id.wage * rate * abs(rounded_diff), 0)
                        total_amount -= amt

                rec.guarantor_id.gratuity_amount = total_amount
