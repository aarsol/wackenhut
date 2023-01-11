from odoo import api, fields, models, tools


class HRTopsheetDeduction(models.TransientModel):
    _name = 'hr.topsheet.deduction'
    _description = 'Top Sheet Deduction Wiz'

    top_sheet_category_id = fields.Many2one('top.sheet.category',string='Top Sheet Category')
    start_date = fields.Date(string='Date From', required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'hr.topsheet.deduction',
            'form': data
        }
        return self.env.ref('aarsol_hr_ext.action_report_topsheet_deduction').with_context(landscape=True).report_action(self,
                                                                                                                 data=datas,
                                                                                                                 config=False)
