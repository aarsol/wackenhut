from odoo import api, fields, models
import pdb


class HrTopsheetAllowancesReport(models.AbstractModel):
    _name = 'report.aarsol_hr_ext.topsheet_allowance_report'
    _description = 'Allowances Report'

    @api.model
    def _get_report_values(self, docsid, data=None, paper=None):
        top_sheet_category_id = data['form']['top_sheet_category_id'] and data['form']['top_sheet_category_id'][
            0] or False

        start_date = data['form']['start_date'] and data['form']['start_date'] or False
        current_user = self.env.user
        start_date = fields.Date.from_string(start_date)

        slips_obj = self.env['hr.payslip']
        recs = slips_obj.search([('date_from', '<=', start_date), ('date_to', '>=', start_date),
                                 ('top_sheet_category_id', '=', top_sheet_category_id)])

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

        search_section = self.env['hr.section'].search([('top_sheet_category_id', '=', top_sheet_category_id)])
        for sec in search_section:

            slips = recs.filtered(lambda l: l.section_id.id == sec.id)
            total_allowances = self.env['hr.payslip.line'].search([('slip_id', 'in', slips.mapped('id'))])
            add_line=[]
            add_line.append(sec.name)
            for rec in allowance_list:
                value = total_allowances.filtered(lambda l: l.name == rec)
                amount =0
                for amu in value:
                    amount += amu.amount
                add_line.append(amount)
            data_list.append(add_line)

        total_list = []
        if data_list:
            for ind in range(len(data_list[0]) - 1):
                amount = 0
                for total in range(len(data_list)):
                    amount += data_list[total][ind + 1]
                total_list.append(amount)

        report = self.env['ir.actions.report']._get_report_from_name('aarsol_hr_ext.topsheet_allowance_report')

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
