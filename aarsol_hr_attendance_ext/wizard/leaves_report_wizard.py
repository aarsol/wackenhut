from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
from io import StringIO, BytesIO
import io
import pdb

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class LeaveReportWizard(models.TransientModel):
    _name = 'leaves.report.wizard'
    _description = 'Leaves Report Wizard'

    date_from = fields.Date('From Date (Request)', required=True, default=fields.Date.today() + relativedelta.relativedelta(months=-5))
    date_to = fields.Date('To Date (Request)', required=True, default=fields.Date.today())
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id.id)

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Salary Sheet")
        style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
        style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
        worksheet.write_merge(0, 1, 0, 9, "Employee Leaves Report", style=style_title)

        row = 3
        col = 0

        # col width
        col0 = worksheet.col(0)
        col0.width = 256 * 8
        col1 = worksheet.col(1)
        col1.width = 256 * 15
        col2 = worksheet.col(2)
        col2.width = 256 * 35
        col3 = worksheet.col(3)
        col3.width = 256 * 30
        col4 = worksheet.col(4)
        col4.width = 256 * 25
        col5 = worksheet.col(5)
        col5.width = 256 * 25
        col6 = worksheet.col(6)
        col6.width = 256 * 25
        col7 = worksheet.col(7)
        col7.width = 256 * 25
        col8 = worksheet.col(8)
        col8.width = 256 * 25
        col9 = worksheet.col(9)
        col9.width = 256 * 25

        table_header = ['Sr#', 'EMP#', 'Name', 'Department', 'Request Date', 'Leave Type', 'Start Date', 'End Date', 'Days', 'Leave Status']
        for i in range(10):
            worksheet.write(row, col, table_header[i], style=style_table_header)
            col += 1
        holidays = self.env['hr.leave'].search([('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to), ('state', '!=', 'refuse')], order='employee_id, create_date')

        sr = 1
        for holiday in holidays:
            row += 1
            col = 0
            worksheet.write(row, col, sr)
            col += 1
            worksheet.write(row, col, holiday.employee_id.code and holiday.employee_id.code or '')
            col += 1
            worksheet.write(row, col, holiday.employee_id.name)
            col += 1
            worksheet.write(row, col, holiday.employee_id.department_id.name)
            col += 1
            worksheet.write(row, col, holiday.create_date and holiday.create_date.strftime("%d-%m-%Y"))
            col += 1

            worksheet.write(row, col, holiday.holiday_status_id.name)
            col += 1
            worksheet.write(row, col, holiday.date_from and holiday.date_from.strftime('%d-%m-%Y') or '-')
            col += 1
            worksheet.write(row, col, holiday.date_to and holiday.date_to.strftime('%d-%m-%Y') or '-')
            col += 1
            worksheet.write(row, col, holiday.number_of_days)
            col += 1
            if holiday.state=='validate':
                worksheet.write(row, col, 'Approved')
            sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)

        wiz_id = self.env['leaves.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Leaves Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Leaves Report Save Form',
            'res_model': 'leaves.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[False, 'form']],
            'res_id': wiz_id.id,
            'target': 'new',
            'context': self._context,
        }


class leaves_report_save_wizard(models.TransientModel):
    _name = "leaves.report.save.wizard"
    _description = "Leave Report Save Wizard"

    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)
