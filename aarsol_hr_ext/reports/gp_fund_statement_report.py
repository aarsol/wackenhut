from odoo import api, fields, models
import pdb


class GpFundStatementReport(models.AbstractModel):
    _name = 'report.aarsol_hr_ext.gp_fund_statement_report'
    _description = 'Gp Fund Statement Report'

    @api.model
    def _get_report_values(self, docsid, data=None, paper=None):
        employee_id = data['form']['employee_id'] and data['form']['employee_id'][0] or False
        start_date = data['form']['start_date'] and data['form']['start_date'] or False
        end_date = data['form']['end_date'] and data['form']['end_date'] or False
        current_user = self.env.user
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        gp_search = self.env['hr.gp.fund'].search(
            [('employee_id', '=', employee_id)])
        opening_balance = 0

        opening_balance_search = gp_search.gp_line_ids.filtered(lambda l: l.month < start_date).sorted(
            key=lambda r: r.month, reverse=True)
        if opening_balance_search:
            opening_balance = opening_balance_search[0].running_balance + gp_search.profit_amount
        else:
            opening_balance = gp_search.opening_balance

        search_statements = self.env['hr.gp.fund.line'].search(
            [('gp_id', '=', gp_search.id), ('month', '>=', start_date), ('month', '<=', end_date)])

        search_balance= search_statements.sorted(
            key=lambda r: r.month, reverse=True)

        start_year = start_date.strftime('%Y')
        end_year = end_date.strftime('%Y')

        report = self.env['ir.actions.report']._get_report_from_name('aarsol_hr_ext.gp_fund_statement_report')

        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'search_statements': search_statements or False,
            'company': current_user.company_id or False,
            'start_year': start_year or False,
            'end_year': end_year or False,
            'gp_search': gp_search or False,
            'opening_balance': opening_balance or False,
            'search_balance': search_balance or False,

        }
        return docargs
