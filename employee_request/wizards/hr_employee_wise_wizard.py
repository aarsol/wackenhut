import pdb

from odoo import models, fields, api


class HREmployeeWise(models.TransientModel):
    _name = 'hr.employee.wise.wizard'
    _description = 'HR Employee Wise Attendance Wizard'

    employee = fields.Many2one("hr.employee", 'Employee')
    department = fields.Many2one("hr.department", 'Department')
    is_check = fields.Boolean(string="Is Check")

    def print_report(self):
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'hr.employee.wise.wizard',
            'form': data
        }
        return self.env.ref("employee_request.action_hr_employee_wise_reportzzz").report_action(self,
                                                                                                          data=datas)
