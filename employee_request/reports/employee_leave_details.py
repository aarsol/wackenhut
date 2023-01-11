from odoo import api, models


class HsaShortCourse(models.AbstractModel):
    _name = 'report.timeoff_ext.employee_leave_detail_report_id'
    _description = 'Employee Leave Record Details'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.employee'].browse(docids[0])
        for rec in docs:
            leave_record = self.env['hr.leave.allocation'].search([('employee_id', '=', rec.name)])

        return {
            'doc_model': 'timeoff_ext',
            'data': data,
            'docs': docs,
            'leave_record': leave_record,
        }
