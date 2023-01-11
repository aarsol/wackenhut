# -*- coding: utf-8 -*-
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _

import logging

_logger = logging.getLogger(__name__)
from io import StringIO
import io
from odoo.exceptions import UserError, ValidationError
import pdb

# try:
#     import csv
# except ImportError:
#     _logger.debug('Cannot `import csv`.')

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


# if row[7].ctype == 3:  # Date
# if row[7]:
#     date_value = xlrd.xldate_as_tuple(row[7], workbook.datemode)
#     grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
#     registration.grade_date = grade_date


class HRDataImportWizard(models.TransientModel):
    _name = "hr.data.import.wizard"
    _description = 'HR Data Import Wizard'

    file = fields.Binary('File')

    def import_hostel_data(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)

        for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
            _logger.info('Employee Record of %s of %s' % (row_num, sheet.nrows))
            row = sheet.row_values(row_num)
            old_list = str(row[0]).split('.')
            old_id = old_list[0]

            employee_id = self.env['hr.employee'].search([('code', '=', old_id)])
            if employee_id:
                employee_contract = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)],
                                                                   order='id desc', limit=1)
                if employee_contract:
                    employee_contract.wage =  row[2] and int(row[2]) or 0


                    #Conveyance Allowance
                    convey_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 218)
                    if convey_allw_id:
                        if len(convey_allw_id) > 1:
                            convey_allw_id[1].sudo().unlink()
                        convey_allw_id[0].amount = row[3] and int(row[3]) or 0
                    if not convey_allw_id and row[3] and int(row[3]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 218,
                            'amount': int(row[3])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Medical Allowance
                    med_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 209)
                    if med_allw_id:
                        med_allw_id.amount = row[4] and int(row[4]) or 0
                    if not med_allw_id and row[4] and int(row[4]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 209,
                            'amount': int(row[4])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Computer Allowance
                    comp_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 194)
                    if comp_allw_id:
                        comp_allw_id.amount = row[5] and int(row[5]) or 0
                    if not comp_allw_id and row[5] and int(row[5]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 194,
                            'amount': int(row[5])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # ARA-2017  (1.7.2017 10%)
                    ara2017_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 211)
                    if ara2017_allw_id:
                        ara2017_allw_id.amount = row[6] and int(row[6]) or 0

                    if not ara2017_allw_id and row[6] and int(row[6]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 211,
                            'amount': int(row[6])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Adhoc Relief Allowance 2018 (1.7.2018 10%)
                    ara2018_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 212)
                    if ara2018_allw_id:
                        ara2018_allw_id.amount = row[7] and int(row[7]) or 0
                    if not ara2018_allw_id and row[7] and int(row[7]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 212,
                            'amount': int(row[7])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)


                    # Adhoc Relief Allowance 2019 (1.7.2019 10%)
                    ara2019_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 225)
                    if ara2019_allw_id:
                        ara2019_allw_id.amount = row[8] and int(row[8]) or 0
                    if not ara2019_allw_id and row[8] and int(row[8]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 225,
                            'amount': int(row[8])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # ARA-2016 10%
                    ara2016_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 216)
                    if ara2016_allw_id:
                        ara2016_allw_id.amount = row[9] and int(row[9]) or 0
                    if not ara2016_allw_id and row[9] and int(row[9]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 216,
                            'amount': int(row[9])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Housing Subsidy
                    subsidy_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 222)
                    if subsidy_allw_id:
                        if len(subsidy_allw_id) > 1:
                            subsidy_allw_id[1].sudo().unlink()
                        subsidy_allw_id[0].amount = row[10] and int(row[10]) or 0
                    if not subsidy_allw_id and row[10] and int(row[10]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 222,
                            'amount': int(row[10])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Personal Pay
                    pp_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 186)
                    if pp_allw_id:
                        pp_allw_id.amount = row[11] and int(row[11]) or 0
                    if not pp_allw_id and row[11] and int(row[11]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 186,
                            'amount': int(row[11])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Senior Post Allowance
                    senior_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 217)
                    if senior_allw_id:
                        senior_allw_id.amount = row[12] and int(row[12]) or 0
                    if not senior_allw_id and row[12] and int(row[12]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 217,
                            'amount': int(row[12])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Entertainment Allowance
                    enter_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 219)
                    if enter_allw_id:
                        enter_allw_id.amount = row[13] and int(row[13]) or 0
                    if not enter_allw_id and row[13] and int(row[13]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 219,
                            'amount': int(row[13])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Orderly Allowance
                    orderly_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 220)
                    if orderly_allw_id:
                        orderly_allw_id.amount = row[14] and int(row[14]) or 0
                    if not orderly_allw_id and row[14] and int(row[14]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 220,
                            'amount': int(row[14])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # House Rent Allowance
                    rent_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 172)
                    if rent_allw_id:
                        rent_allw_id.amount = row[15] and int(row[15]) or 0
                    if not rent_allw_id and row[15] and int(row[15]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 172,
                            'amount': int(row[15])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Qualification Pay / Ph.D
                    qual_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 188)
                    if qual_allw_id:
                        qual_allw_id.amount = row[16] and int(row[16]) or 0
                    if not qual_allw_id and row[16] and int(row[16]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 188,
                            'amount': int(row[16])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Brain Drain
                    bd_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 208)
                    if bd_allw_id:
                        bd_allw_id.amount = row[17] and int(row[17]) or 0
                    if not bd_allw_id and row[17] and int(row[17]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 208,
                            'amount': int(row[17])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Charge Allownce (Dean/Chairman/HOD)
                    dean_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 196)
                    if dean_allw_id:
                        dean_allw_id.amount = row[18] and int(row[18]) or 0
                    if not dean_allw_id and row[18] and int(row[18]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 196,
                            'amount': int(row[18])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Teaching Allowance
                    teaching_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 221)
                    if teaching_allw_id:
                        teaching_allw_id.amount = row[20] and int(row[20]) or 0
                    if not teaching_allw_id and row[20] and int(row[20]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 221,
                            'amount': int(row[20])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Integrated Allowance
                    integ_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 201)
                    if integ_allw_id:
                        integ_allw_id.amount = row[21] and int(row[21]) or 0
                    if not integ_allw_id and row[21] and (row[21]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 201,
                            'amount': int(row[21])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Special Allowance.
                    sp_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 198)

                    if sp_allw_id:

                        if len(sp_allw_id) > 1:
                            sp_allw_id[1].sudo().unlink()
                        sp_allw_id[0].amount = row[22] and int(row[22]) or 0
                    if not sp_allw_id and row[22] and int(row[22]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 198,
                            'amount': int(row[22])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Fuel Allowance.
                    fuel_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 200)
                    if fuel_allw_id:
                        fuel_allw_id.amount = row[23] and int(row[23]) or 0
                    if not fuel_allw_id and row[23] and int(row[23]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 200,
                            'amount': int(row[23])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Private sec
                    private_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 202)
                    if private_allw_id:
                        private_allw_id.amount = row[24] and int(row[24]) or 0
                    if not private_allw_id and row[24] and int(row[24]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 202,
                            'amount': int(row[24])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # VC Allowance
                    vc_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 203)
                    if vc_allw_id:
                        vc_allw_id.amount = row[25] and int(row[25]) or 0
                    if not vc_allw_id and row[25] and int(row[25]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 203,
                            'amount': int(row[25])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Pay of Contract Staf
                    payst_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 189)
                    if payst_allw_id:
                        payst_allw_id.amount = row[56] and int(row[56]) or 0
                    if not payst_allw_id and row[56] and int(row[56]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 189,
                            'amount': int(row[56])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Special Allowance Adjustment

                    spa_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 177)
                    if spa_allw_id:
                        spa_allw_id.amount = row[57] and int(row[57]) or 0
                    if not spa_allw_id and row[57] and int(row[57]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 177,
                            'amount': int(row[57])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)

                    # Others Allowance

                    others_allw_id = employee_contract.allowance_ids.filtered(lambda a: a.allowance_id.id == 191)
                    if others_allw_id:
                        others_allw_id.amount = row[58] and int(row[58]) or 0
                    if not others_allw_id and row[58] and int(row[58]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'allowance_id': 191,
                            'amount': int(row[58])
                        }
                        self.env['hr.emp.salary.allowances'].create(values)





                    ########################################################
                    #                  DEDUCTIONS                          #
                    #######################################################

                    # Water Charges Peshawar.

                    water_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 45)

                    if water_id:
                        if len(water_id) > 1:
                            water_id[1].sudo().unlink()
                        water_id[0].amount = row[27] and int(row[27]) or 0
                    if not water_id and row[27] and int(row[27]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 45,
                            'amount': int(row[27])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Electricity Charges Peshawar E1.
                    elec_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 46)
                    if elec_id:
                        if len(elec_id) > 1:
                            elec_id[1].sudo().unlink()
                        elec_id[0].amount = row[28] and int(row[28]) or 0
                    if not elec_id and row[28] and int(row[28]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 46,
                            'amount': int(row[28])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Income tax.
                    income_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 86)
                    if income_id:

                        if len(income_id) > 1:
                            income_id[1].sudo().unlink()
                        income_id[0].amount = row[29] and int(row[29]) or 0
                    if not income_id and row[29] and int(row[29]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 86,
                            'amount': int(row[29])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)




                    # GPF.
                    gpf_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 75)
                    if gpf_id:
                        if len(gpf_id) > 1:
                            gpf_id[1].sudo().unlink()
                        gpf_id[0].amount = row[30] and int(row[30]) or 0
                    if not gpf_id and row[30] and int(row[30]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 75,
                            'amount': int(row[30])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Benevolent Fund
                    bene_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 76)
                    if bene_id:
                        if len(bene_id) > 1:
                            bene_id[1].sudo().unlink()
                        bene_id[0].amount = row[31] and int(row[31]) or 0
                    if not bene_id and row[31] and int(row[31]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 76,
                            'amount': int(row[31])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Group Insurance
                    ins_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 77)
                    if ins_id:
                        if len(ins_id) > 1:
                            ins_id[1].sudo().unlink()
                        ins_id.amount = row[32] and int(row[32]) or 0
                    if not ins_id and row[32] and int(row[32]) > 0:

                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 77,
                            'amount': int(row[32])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Union Fund -2
                    union_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 78)
                    if union_id:
                        union_id.amount = row[33] and int(row[33]) or 0
                    if not union_id and row[33] and int(row[33]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 78,
                            'amount': int(row[33])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Union Fund -1
                    union1_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 80)
                    if union1_id:
                        union1_id.amount = row[34] and int(row[34]) or 0
                    if not union1_id and row[34] and row[34] and int(row[34]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 80,
                            'amount': int(row[34])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Sui Gas Charges
                    gas_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 62)
                    if gas_id:
                        gas_id.amount = row[37] and int(row[37]) or 0
                    if not gas_id and row[37] and row[37] and int(row[37]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 62,
                            'amount': int(row[37])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Electricity Charges E-2 Engineering
                    elec1_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 48)
                    if elec1_id:
                        elec1_id.amount = row[40] and int(row[40]) or 0
                    if not elec1_id and row[40] and row[40] and int(row[40]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 48,
                            'amount': int(row[40])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)



                    # Water Tax-2 Engineering
                    water1_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 49)
                    if water1_id:
                        water1_id.amount = row[41] and int(row[41]) or 0
                    if not water1_id and row[41] and row[41] and int(row[41]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 49,
                            'amount': int(row[41])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Upkeep
                    ukeep_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 82)
                    if ukeep_id:
                        ukeep_id.amount = row[43] and int(row[43]) or 0
                    if not ukeep_id and row[43] and row[43] and int(row[43]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 82,
                            'amount': int(row[43])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # Endowment
                    # fund

                    endo_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 56)
                    if endo_id:
                        endo_id.amount = row[51] and int(row[51]) or 0
                    if not endo_id and row[51] and row[51] and int(row[51]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 56,
                            'amount': int(row[51])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # House Rent Engineering

                    house_rent_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 72)

                    if house_rent_id:
                        house_rent_id.amount = row[52] and int(row[52]) or 0
                    if not house_rent_id and row[52] and row[52] and int(row[52]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 72,
                            'amount': int(row[52])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)

                    # C.A
                    # Deduction

                    ca_id = employee_contract.deduction_ids.filtered(lambda a: a.deduction_id.id == 55)

                    if ca_id:
                        ca_id.amount = row[49] and int(row[49]) or 0
                    if not ca_id and row[49] and row[49] and int(row[49]) > 0:
                        values = {
                            'employee_id': employee_id.id,
                            'contract_id': employee_contract.id,
                            'deduction_id': 55,
                            'amount': int(row[49])
                        }
                        self.env['hr.emp.salary.deductions'].create(values)