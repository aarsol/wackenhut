from odoo import api, fields, models
import pdb


class HrAllowancesReport(models.AbstractModel):
    _name = 'report.aarsol_hr_ext.allowance_report'
    _description = 'Allowances Report'

    @api.model
    def _get_report_values(self, docsid, data=None, paper=None):
        designation_id = data['form']['designation_id'] and data['form']['designation_id'][0] or False
        section_id = data['form']['section_id'] and data['form']['section_id'][0] or False
        department_id = data['form']['department_id'] and data['form']['department_id'][0] or False
        search_by = data['form']['search_by'] and data['form']['search_by'] or False

        start_date = data['form']['start_date'] and data['form']['start_date'] or False
        current_user = self.env.user
        start_date = fields.Date.from_string(start_date)

        slips_obj = self.env['hr.payslip']
        if search_by == 'overall':
            recs = slips_obj.search([('date_from', '<=', start_date), ('date_to', '>=', start_date)])
        if search_by == 'designation':
            recs = slips_obj.search([('date_from', '<=', start_date), ('date_to', '>=', start_date),
                                     ('designation_id', '=', designation_id)])

        if search_by == 'department':
            recs = slips_obj.search([('date_from', '<=', start_date), ('date_to', '>=', start_date),
                                     ('department_id', '=', department_id)])

        if search_by == 'section':
            recs = slips_obj.search([('date_from', '<=', start_date), ('date_to', '>=', start_date),
                                     ('section_id', '=', section_id)])
        allowance_list = []
        allowance_list_lids = []
        for payslip in recs:
            allowance = payslip.line_ids.filtered(
                lambda l: l.category_id.name in ('Allowance', 'Basic'))
            for allow in allowance:
                if len(allowance_list) == 0:
                    allowance_list.append(allow.name)
                    allowance_list_lids.append(allow.id)
                else:
                    for record in allowance:
                        if record.name not in allowance_list:
                            allowance_list.append(record.name)
                            allowance_list_lids.append(record.id)
            # gross =payslip.line_ids.filtered(
            #     lambda l: l.category_id.name =='Gross')
            # if gross.name not in allowance_list:
        allowance_list.append('Gross')

        data_list = []
        for payslip in recs:
            line = []
            allowance = payslip.line_ids.filtered(
                lambda l: l.category_id.name in ('Allowance', 'Basic', 'Gross') and l.name in allowance_list)

            for allow in allowance:
                if allow.name in allowance_list:
                    line.append(
                        {
                            'name': allow.name,
                            'amount': allow.amount, })
            add_line = []

            add_line.append(payslip.employee_id.name)
            for rec in allowance_list:
                value = allowance.filtered(lambda l: l.name == rec)
                if value:
                    add_line.append(value.amount)
                else:
                    add_line.append(0)

            data_list.append(add_line)
        total_list = []
        if data_list:
            for ind in range(len(data_list[0]) - 1):

                amount = 0
                for total in range(len(data_list)):
                    amount += data_list[total][ind + 1]
                total_list.append(amount)

        report = self.env['ir.actions.report']._get_report_from_name('aarsol_hr_ext.allowance_report')

        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'company': current_user.company_id or False,
            'allowance_list': allowance_list or False,
            'data_list': data_list or False,
            'start_date': start_date or False,
            'total_list': total_list or False,

        }
        return docargs
