from odoo import api, fields, models, tools


class HRdeductionminiserailWiz(models.TransientModel):
    _name = 'hr.ministerial.deduction.wiz'
    _description = 'Ministerial Deduction Wiz'

    start_date = fields.Date(string='Date From', required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'hr.ministerial.deduction.wiz',
            'form': data
        }
        return self.env.ref('aarsol_hr_ext.action_report_deduction_ministerial').with_context(landscape=True).report_action(self,
                                                                                                                 data=datas,
                                                                                                                 config=False)
