import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from odoo import models, fields, api, _
import pdb


def parse_date(td):
    resYear = float(td.days) / 365.0
    resMonth = (resYear - int(resYear)) * 365.0 / 30.0
    resDays = int((resMonth - int(resMonth)) * 30)
    resYear = int(resYear)
    resMonth = int(resMonth)
    return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (resMonth and (str(resDays) + "D") or "")


class HREmployeeMedical(models.Model):
    _name = 'hr.employee.medical'
    _description = 'Employee Medical'

    disease = fields.Char('Disease', required=1)
    appointment_date = fields.Char('Appointment Date')
    hospital = fields.Char('Hospital')
    employee_id = fields.Many2one('hr.employee', 'Employee')


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    medical_ids = fields.One2many('hr.employee.medical', 'employee_id', 'Medical History', groups="hr.group_hr_user")


class HREmployeeOperationArea(models.Model):
    _name = 'hr.employee.operation.area'
    _description = 'Employee Operation Areas'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Operation Area')
    code = fields.Char('Code')


class HREmployeeFamily(models.Model):
    _name = 'hr.employee.family'
    _description = 'Employee Family'

    name = fields.Char('Name of Family Member', required=1)
    relationship = fields.Char('Relationship with employee')
    phone_no = fields.Char('Contact No')
    employee_id = fields.Many2one('hr.employee', 'Employee')


class hr_experience(models.Model):
    _name = 'hr.experience'

    def _total_experience_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                start = datetime.strptime(str(rec.start_date), OE_DFORMAT)
                end = datetime.strptime(str(rec.end_date), OE_DFORMAT)
                delta = end - start
                rec.total_experience = parse_date(delta)

    name = fields.Char("Company Name")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    position = fields.Char("Position")
    salary = fields.Float("Salary")
    currency = fields.Char("Currency")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    total_experience = fields.Char(compute='_total_experience_days', string="Total Experience", help="Auto Calculated")
    reporting_to = fields.Char("Reporting To")
    reason_to_leave = fields.Text("Reason For Leaving")
    responsibilities = fields.Text("Responsibilities")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    medical_ids = fields.One2many('hr.employee.medical', 'employee_id', 'Medical History')
    operation_area_id = fields.Many2one('hr.employee.operation.area', string='Operation Area')
    family_ids = fields.One2many('hr.employee.family', 'employee_id', 'Family')
    joining_date = fields.Date('Date Of Joining')
    leaving_date = fields.Date('Date Of Leaving')
    academic_ids = fields.One2many('hr.employee.academic', 'employee_id', 'Academics')
    experience_ids = fields.One2many('hr.experience', 'employee_id', 'Experience information')
    age = fields.Char("Age", compute='_compute_age')

    def _compute_age(self):
        for rec in self:
            if rec.birthday:
                start = datetime.strptime(str(rec.birthday), OE_DFORMAT)
                end = datetime.strptime(str(time.strftime(OE_DFORMAT)), OE_DFORMAT)
                delta = end - start
                rec.age = parse_date(delta)


class HREmployeeAcademic(models.Model):
    _name = 'hr.employee.academic'
    _description = 'Employee Academics'

    degree_level = fields.Selection([('matric', 'Matric'),
                                     ('inter', 'Intermediate'),
                                     ('undergraduate', 'Graduate'),
                                     ('postgraduate', 'Postgraduate'),
                                     ('professional_education', 'Professional Education')
                                     ], 'Degree Level', required=1)
    degree = fields.Char('Degree')
    year = fields.Char('Passing Year')
    board = fields.Char('Board Name')
    subjects = fields.Char('Subjects')
    total_marks = fields.Float('Total Marks/CGPA', required=1)
    obtained_marks = fields.Float('Obtained Marks/CGPA', required=1)
    employee_id = fields.Many2one('hr.employee', 'Employee')
