from odoo import api, fields, models
import pdb


class HrDeductionReport(models.AbstractModel):
    _name = 'report.aarsol_hr_ext.deduction_report'
    _description = 'Deduction Report'

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
        deduction_list = []
        # deduction_list_lids = []
        for payslip in recs:
            deduction = payslip.line_ids.filtered(
                lambda l: l.category_id.name in ('Deduction'))
            for dedu in deduction:
                if len(deduction_list) == 0:
                    deduction_list.append(dedu.name)
                    # deduction_list_lids.append(dedu.id)
                else:
                    for record in deduction:
                        if record.name not in deduction_list:
                            deduction_list.append(record.name)

        deduction_list.append('Total Deduction')
        deduction_list.append('Net Salary')

        data_list = []
        gross = 0
        gross_list = []
        for payslip in recs:
            line = []
            deduction = payslip.line_ids.filtered(
                lambda l: l.category_id.name in ('Deduction', 'Net') and l.name in deduction_list)

            for dedu in deduction:
                if dedu.name in deduction_list:
                    line.append(
                        {
                            'name': dedu.name,
                            'amount': dedu.amount, })
            add_line = []

            add_line.append(payslip.employee_id.name)

            total_deduction = 0
            search_deduction = payslip.line_ids.filtered(
                lambda l: l.category_id.name == 'Deduction')
            for total in search_deduction:
                total_deduction += total.amount

            for rec in deduction_list:
                value = deduction.filtered(lambda l: l.name == rec)
                if value and rec == 'Net Salary':
                    add_line.append(value.amount)
                elif value and rec != 'Net Salary':
                    add_line.append(-1 * value.amount)

                elif rec == 'Total Deduction':
                    add_line.append(-1 * total_deduction)

                else:
                    add_line.append(0)

            data_list.append(add_line)


            search_gross = payslip.line_ids.filtered(
                lambda l: l.category_id.name == 'Gross')
            for gr in search_gross:
                gross += gr.amount
        gross_list.append(gross)


        total_list = []
        if data_list:
            for ind in range(len(data_list[0]) - 1):

                amount = 0
                for total in range(len(data_list)):
                    amount += data_list[total][ind + 1]
                total_list.append(amount)

        report = self.env['ir.actions.report']._get_report_from_name('aarsol_hr_ext.deduction_report')

        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'company': current_user.company_id or False,
            'deduction_list': deduction_list or False,
            'data_list': data_list or False,
            'start_date': start_date or False,
            'total_list': total_list or False,
            'gross_list': gross_list or False,

        }
        return docargs
