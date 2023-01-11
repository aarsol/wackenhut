# -*- coding: utf-8 -*-
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from io import StringIO
import io
from odoo.exceptions import UserError, ValidationError
import pdb

import logging

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
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


class HREmpSalaryInputsImportWizard(models.TransientModel):
    _name = "hr.emp.salary.inputs.import.wizard"
    _description = 'Import Salary Inputs From Excel File'

    file = fields.Binary('File')
    sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'),
                                     ('system', 'Use System Default Sequence Number')
                                     ], string='Sequence Option', default='custom')
    import_option = fields.Selection([('csv', 'CSV File'),
                                      ('xls', 'XLS File')
                                      ], string='Select', default='xls')

    def import_emp_salary_inputs_action(self):
        """Load data from the CSV file."""
        if self.import_option=='csv':
            keys = ['barcode']
            data = base64.b64decode(self.file)
            file_input = io.StringIO(data.decode("utf-8"))
            file_input.seek(0)
            reader_info = []
            reader = csv.reader(file_input, delimiter=',')

            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            values = {}
            for i in range(len(reader_info)):
                # val = {}
                field = list(map(str, reader_info[i]))
                values = dict(zip(keys, field))
                if values:
                    if i==0:
                        continue
                    else:
                        values.update({'option': self.import_option, 'seq_opt': self.sequence_opt})
                        res = self.make_sale(values)
        else:
            ret_recs = self.env['hr.emp.salary.inputs']
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)

            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = list(map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                    emp_code = line[0]
                    emp_code_vals = emp_code.split('.')
                    if emp_code_vals:
                        emp_code = emp_code_vals[0]
                    if emp_code:
                        employee_id = self.env['hr.employee'].search([('code', '=', emp_code), '|', ('active', '=', True), ('active', '=', False)])
                        if not employee_id:
                            raise UserError(_('%s Employee code not Found in the System.') % (emp_code))
                        input_category = self.env['hr.salary.inputs'].search([('name', '=', line[1])])
                        if not input_category:
                            raise UserError(_('Salary Input Category %s not found, please recheck it.') % (line[1]))

                        if line[3]:
                            date_value = xlrd.xldate_as_tuple(float(line[3]), workbook.datemode)
                            inp_date = date(*date_value[:3]).strftime('%Y-%m-%d')

                        input_id = self.env['hr.emp.salary.inputs'].create({
                            'employee_id': employee_id.id,
                            'name': line[1],
                            'amount': float(line[2]),
                            'state': 'confirm',
                            'input_id': input_category and input_category.id or False,
                            'date': inp_date,
                        })
                        ret_recs += input_id
                    else:
                        raise UserError('Employee Code not Found')

            # if ret_recs:
            #     ret_recs_list = ret_recs.mapped('id')
            #     form_view = self.env.ref('aarsol_hr_ext.view_hr_emp_salary_inputs_form')
            #     tree_view = self.env.ref('aarsol_hr_ext.view_hr_emp_salary_inputs_tree')
            #     return {
            #         'domain': [('id', 'in', ret_recs_list)],
            #         'name': _('Employee Salary Inputs'),
            #         'view_type': 'tree',
            #         'view_mode': 'tree,form',
            #         'res_model': 'hr.emp.salary.inputs',
            #         'view_id': False,
            #         'views': [
            #             (tree_view and tree_view.id or False, 'tree'),
            #             (form_view and form_view.id or False, 'form'),
            #         ],
            #         'type': 'ir.actions.act_window'
            #     }
            # else:
            #     return {'type': 'ir.actions.act_window_close'}
