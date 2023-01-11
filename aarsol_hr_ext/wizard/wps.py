from datetime import datetime

from odoo import models, fields, api

import io
import base64
import csv
import pdb


class hr_payslip_wps(models.TransientModel):
    _name = 'hr.payslip.wps'
    _description = 'WPS for Bank'

    filedata = fields.Binary('File')
    filename = fields.Char('Filename', size=64, readonly=True)
    date = fields.Date('Date')


    def get_wps(self):
        slips_obj = self.env['hr.payslip']
        data = self.read([])[0]

        recs = slips_obj.search([('date_from', '<=', self.date), ('date_to', '>=', self.date)])

        result = []
        result.append(['Sr#', 'Employee #', 'Basic Pay Scale', 'Name', 'Designation', 'Department', 'Section', 'Joining Date',
                       'Basic Salary','A01202 House Rent Allowance','A01203 Conveyance Allowance','A01217 Medical Allowance','A12AE Integrated Allowance',
                       'A01224 Entertainment Allowance','A01244-12 ARA 2019 (1.7.2019 10%)','A01244-11 ARA 2018 (1.7.2018 10%)','A01201 Senior Post Allowance','Teaching Allowance',
                       'A01228 Orderly Allowance','A01244-9 ARA-2016 10%','A01244-10 ARA-2017 (1.7.2017 10%)','A01150-I Brain Drain','A012AA Housing Subsidy', 'A01105 Qualification Pay/ Ph.D',
                       'A01226 Computer Allowance','A01238 Charge Allowance(Dean/Chairman/HOD)','A01279 Special Allowance','A03601 Fuel','U00006 VC Allowance'
                       'U00005 Private sec','A01150 Others','Gross Pay',
                       'Water Charges(Peshawar)','Electricity Charges(Peshawar)',
                       'Electricity Charges(Engineering)','Water Charges(Engineering)','Eid Advance','House Building Adv',
                       'House Rent Adjustment','C.A Deduction','Pension Fund Liability(Contribution)',
                       'Masjid Deduction','Sui Gas Charges','Vehicle Charges','Teaching Allowance(D)','Conveyance Allowance Recovery',
                       'General Provident Fund','House Rent -Engineering','Hostel Rent','GPF','Benevolent Fund',
                       'Group Insurance','Union Fund -2','Union Fund -1','Upkeep' ,'Adjustment', 'Income Tax',
                       'Total Deduction', 'Net Amount',
                       'Account Number'])

        i = 1
        for rec in recs:
            arrear = 0
            gross = 0
            net = 0
            od = 0
            tax = 0
            increment = 0
            h_rent=0
            c_allowance=0
            m_allowance=0
            i_allowance=0
            e_allowance = 0
            ara_2019 =0
            ara_2018 = 0
            sp_allowance=0
            t_allowance=0
            o_allowance=0
            ara_2016=0
            ara_2017=0
            b_drain =0
            h_subsidy=0
            q_phd=0
            comp_allowance=0
            charge_allowance=0
            s_allowance=0
            fuel=0
            vc_allowance=0
            private_sec =0
            other_allowance=0

            for line in rec.line_ids:
                # line.salary_rule_id.category_id.code
                if line.salary_rule_id.code == 'FINC':
                    increment += line.total
                if line.salary_rule_id.code == 'NET':
                    net += line.total
                if line.salary_rule_id.code == 'IT':
                    tax += line.total
                if line.salary_rule_id.code == 'GROSS':
                    gross += line.total
                if line.salary_rule_id.code == 'OD':
                    od += line.total
                if line.salary_rule_id.code == 'ARS':
                    arrear += line.total
                # Allownce Code
                if line.salary_rule_id.code == 'HRA':
                    h_rent += line.total
                if line.salary_rule_id.code == 'CALW':
                    c_allowance += line.total
                if line.salary_rule_id.code == 'MEDALW':
                    m_allowance += line.total
                if line.salary_rule_id.code == 'INTALW':
                    i_allowance += line.total
                if line.salary_rule_id.code == 'ENTALW':
                    e_allowance += line.total
                if line.salary_rule_id.code == 'ARA19':
                    ara_2019 += line.total
                if line.salary_rule_id.code == 'ARA18':
                    ara_2018 += line.total
                if line.salary_rule_id.code == 'SNPALW':
                    sp_allowance += line.total
                if line.salary_rule_id.code == 'TALW':
                    t_allowance += line.total
                if line.salary_rule_id.code == 'ORDALW':
                    o_allowance += line.total
                if line.salary_rule_id.code == 'ARA16':
                    ara_2016 += line.total
                if line.salary_rule_id.code == 'ARA17':
                    ara_2017 += line.total
                if line.salary_rule_id.code == 'BDALW':
                    b_drain += line.total
                if line.salary_rule_id.code == 'HSALW':
                    h_subsidy += line.total
                if line.salary_rule_id.code == 'QA':
                    q_phd += line.total
                if line.salary_rule_id.code == 'COMPA':
                    comp_allowance += line.total
                if line.salary_rule_id.code == 'CHGA':
                    charge_allowance += line.total
                if line.salary_rule_id.code == 'SPALW':
                    s_allowance += line.total
                if line.salary_rule_id.code == 'FLALW':
                    fuel += line.total
                if line.salary_rule_id.code == 'VCALW':
                    vc_allowance += line.total
                if line.salary_rule_id.code == 'PRSALW':
                    private_sec += line.total
                if line.salary_rule_id.code == 'OALW':
                    other_allowance += line.total

            temp = []

            temp.append(str(i))
            temp.append(rec.employee_id.code)
            temp.append(rec.employee_id.payscale_id.name)
            temp.append(rec.employee_id.name)
            temp.append(rec.employee_id.job_title)
            temp.append(rec.employee_id.department_id.name)
            temp.append(rec.employee_id.section_id.name)
            temp.append(rec.contract_id.date_start)

            temp.append(rec.contract_id.wage)
            temp.append(str(h_rent or 0))
            temp.append(str(c_allowance or 0))
            temp.append(str(m_allowance or 0))
            temp.append(str(i_allowance or 0))
            temp.append(str(e_allowance or 0))
            temp.append(str(ara_2019 or 0))
            temp.append(str(ara_2018 or 0))
            temp.append(str(sp_allowance or 0))
            temp.append(str(t_allowance or 0))
            temp.append(str(o_allowance or 0))
            temp.append(str(ara_2016 or 0))
            temp.append(str(ara_2017 or 0))
            temp.append(str(b_drain or 0))
            temp.append(str(h_subsidy or 0))
            temp.append(str(comp_allowance or 0))
            temp.append(str(charge_allowance or 0))
            temp.append(str(s_allowance or 0))
            temp.append(str(fuel or 0))
            temp.append(str(vc_allowance or 0))
            temp.append(str(private_sec or 0))
            temp.append(str(other_allowance or 0))
            temp.append(str(gross))

            # temp.append(str(increment or 0))
            # temp.append(str(arrear or 0))
            #
            # temp.append(str(od or 0))
            # temp.append(str(tax or 0))
            #
            # temp.append(str(net))
            # temp.append(str(rec.employee_id.bank_account_no))

            result.append(temp)
            i = i + 1

        fp = io.StringIO()
        writer = csv.writer(fp)
        for data in result:
            row = []
            for d in data:
                # if isinstance(d, str):
                # 	d = d.replace('\n',' ').replace('\t',' ')
                # 	try:
                # 		d = d.encode('utf-8')
                # 	except:
                # 		pass
                if d is False: d = None
                row.append(d)
            writer.writerow(row)

        fp.seek(0)
        data = fp.read()
        fp.close()

        out = base64.encodestring(data.encode(encoding='utf-8'))  # base64.encodestring(data)
        file_name = 'payroll_' + str(self.date) + '_wps.csv'

        self.write({'filedata': out, 'filename': file_name})

        return {
            'name': 'WPS File',
            'res_model': 'hr.payslip.wps',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'res_id': self.id,
        }
