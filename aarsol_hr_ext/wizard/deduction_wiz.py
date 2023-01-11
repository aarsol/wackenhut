from odoo import api, fields, models, tools


class HRdeductionWiz(models.TransientModel):
    _name = 'hr.deduction.wiz'
    _description = 'Deduction Wiz'

    designation_id = fields.Many2one('hr.job', string='Designation')
    department_id = fields.Many2one('hr.department', string='Department')
    section_id = fields.Many2one('hr.section', string='Section')
    start_date = fields.Date(string='Date From', required=True)
    search_by = fields.Selection(
        [('overall', 'Overall'), ('designation', 'Designation'), ('department', 'Department'), ('section', 'Section')],
        'Search By', default='overall')


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'hr.deduction.wiz',
            'form': data
        }
        return self.env.ref('aarsol_hr_ext.action_report_deduction').with_context(landscape=True).report_action(self,
                                                                                                                 data=datas,
                                                                                                                 config=False)
