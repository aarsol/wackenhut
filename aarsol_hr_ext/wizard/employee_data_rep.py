import pdb
import time
from datetime import date
import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)

from io import StringIO
import io

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


class EmployeeDataRep(models.TransientModel):
    _name = 'employee.data.rep'
    _description = 'Employee Data Report'

    # all_employee = fields.Boolean('All Employee?')
    # officer_crew = fields.Selection([('officer', 'Management'), ('crew', 'CIT Crew')], 'Management/Crew')
    # region_ids = fields.Many2many('cit.region','employee_data_rep_region_rel','emp_data_rep','region_id','Regions')
    # crew_contract = fields.Many2many('cit.crew.contract','employee_data_rep_contract_rel','emp_data_rep','contract_id',string='Crew Contract')
    # employee_type = fields.Selection([
    #     ('cc', 'Crew Chief'),
    #     ('acc', 'Assistant Crew Chief'),
    #     ('driver', 'Driver'),
    #     ('guard', 'Guard'),
    #     ('reliever', 'Reliever'),
    #     ('cmc', 'CMC'),
    #     ('acc_cum_driver', 'ACC CUM Driver'),
    #     ('guard_cum_driver', 'Guard Cum Driver'),
    #     ('female_internee','Female Internee'),
    # ], 'Employee Type')

    # ***** Excel Report *****#

    def make_excel(self):
        # ***** Excel Related Statements *****#
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("ALL EMPLOYEE DATA Report")

        style_title = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_title2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
        style_table_header = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
        style_table_totals = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_date_col = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
        style_date_col2 = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;")

        worksheet.write_merge(0, 1, 0, 31, "Employee DATA ", style=style_title)

        col_0 = worksheet.col(0)
        col_0.width = 256 * 12
        col_1 = worksheet.col(1)
        col_1.width = 256 * 10
        col_2 = worksheet.col(2)
        col_2.width = 256 * 30
        col_3 = worksheet.col(3)
        col_3.width = 256 * 15
        col_4 = worksheet.col(4)
        col_4.width = 256 * 20
        col_5 = worksheet.col(5)
        col_5.width = 256 * 25
        col_6 = worksheet.col(6)
        col_6.width = 256 * 25
        col_7 = worksheet.col(7)
        col_7.width = 256 * 25
        col_8 = worksheet.col(8)
        col_8.width = 256 * 15
        col_9 = worksheet.col(9)
        col_9.width = 256 * 15
        col_10 = worksheet.col(10)
        col_10.width = 256 * 15
        col_11 = worksheet.col(11)
        col_11.width = 256 * 15
        col_12 = worksheet.col(12)
        col_12.width = 256 * 15
        col_13 = worksheet.col(13)
        col_13.width = 256 * 25
        col_14 = worksheet.col(14)
        col_14.width = 256 * 15
        col_15 = worksheet.col(15)
        col_15.width = 256 * 15
        col_16 = worksheet.col(16)
        col_16.width = 256 * 25
        col_17 = worksheet.col(17)
        col_17.width = 256 * 15
        col_18 = worksheet.col(18)
        col_18.width = 256 * 15
        col_19 = worksheet.col(19)
        col_19.width = 256 * 25
        col_20 = worksheet.col(20)
        col_20.width = 256 * 15
        col_21 = worksheet.col(21)
        col_21.width = 256 * 15
        col_22 = worksheet.col(22)
        col_22.width = 256 * 15
        col_23 = worksheet.col(23)
        col_23.width = 256 * 15
        col_24 = worksheet.col(24)
        col_24.width = 256 * 15
        col_25 = worksheet.col(25)
        col_25.width = 256 * 15
        col_26 = worksheet.col(26)
        col_26.width = 256 * 15
        col_27 = worksheet.col(27)
        col_27.width = 256 * 15
        col_28 = worksheet.col(28)
        col_28.width = 256 * 25
        col_29 = worksheet.col(29)
        col_29.width = 256 * 20
        col_30 = worksheet.col(30)
        col_30.width = 256 * 40
        col_31 = worksheet.col(31)
        col_31.width = 256 * 40



        recs = False
        row = 2
        col = 0
        # ***** Table Heading *****#
        table_header = ['DataBase ID', 'ERP CODE', 'Name', 'Bank Name','Title Of Account','Account Number','Date of Birth', 'CNIC','Nationality','Gender','Appointment Date','Department','Section','Designation','Mobile','Martial Status','Email Address','Emergency Contact #','Present Address']
        for i in range(19):
            worksheet.write(row, col, table_header[i], style=style_table_header)
            col += 1
        recs = False

        recs = self.env['hr.employee'].search([])
        # if not self.all_employee:
        #     if self.officer_crew:
        #         domain.append(('officer_crew', '=', self.officer_crew),)
        #     if self.region_ids:
        #         domain.append(('region_id', 'in', self.region_ids.ids), )
        #     if self.crew_contract:
        #         domain.append(('employee_contract_id', 'in', self.crew_contract.ids),)
        #     if self.employee_type:
        #         domain.append(('employee_type', '=', self.employee_type),)

        recs = self.env['hr.employee'].search([])

        i =1
        if recs:
            for rec in recs:
                manager_employee = ''
                mm = False
                mm = self.env['hr.employee'].search([('parent_id','=',rec.id)])
                if mm:
                    manager_employee = 'Manager'
                else:
                    manager_employee = 'Employee'

                row += 1
                col = 0

                worksheet.write(row, col, rec.id, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.code, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.name, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.bank_id and rec.bank_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.bank_account_title and rec.bank_account_title or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.bank_account_no and rec.bank_account_no or '', style=style_date_col)
                # col += 1
                # worksheet.write(row, col, rec.father_name, style=style_date_col)
                # col += 1
                # worksheet.write(row, col, rec.mother_name, style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.birthday and datetime.datetime.strptime(str(rec.birthday), '%Y-%m-%d').strftime('%d/%m/%Y') or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.cnic, style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.country_id and rec.country_id.name or '',style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.gender and rec.gender or '', style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.joining_date and datetime.datetime.strptime(str(rec.joining_date), '%Y-%m-%d').strftime('%d/%m/%Y') or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.department_id and rec.department_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.section_id and rec.section_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.job_title, style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.mobile_phone and rec.mobile_phone or '', style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.marital and rec.marital or '', style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.work_email and rec.work_email or '', style=style_date_col)
                col += 1
                # worksheet.write(row, col, rec.parent_id and rec.parent_id.name or '', style=style_date_col)
                # col += 1
                worksheet.write(row, col, ((rec.emergency_contact and rec.emergency_contact) or (rec.emergency_phone and rec.emergency_phone) or ''), style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.address_home_id and rec.address_home_id.name or '', style=style_date_col)
                col += 1

                i += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['employee.data.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Employee Data Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Data Report',
            'res_model': 'employee.data.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }


class Employee_data_wizard(models.TransientModel):
    _name = "employee.data.save.wizard"
    _description = 'Employee Data Save Wizard'

    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)