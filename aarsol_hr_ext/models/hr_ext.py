import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json
import pdb


def parse_date(td):
    resYear = float(td.days) / 365.0
    resMonth = (resYear - int(resYear)) * 365.0 / 30.0
    resDays = int((resMonth - int(resMonth)) * 30)
    resYear = int(resYear)
    resMonth = int(resMonth)
    return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (resMonth and (str(resDays) + "D") or "")


class HRJob(models.Model):
    _inherit = 'hr.job'

    section_id = fields.Many2one('hr.section', 'Section')


class HRSection(models.Model):
    _name = 'hr.section'
    _description = 'HR Section'

    name = fields.Char('Section Name')
    top_sheet_category_id = fields.Many2one('top.sheet.category', string='Top Sheet Category')
    employee_ids = fields.One2many('hr.employee', 'section_id', 'Employees')


class HRTopSheetCategory(models.Model):
    _name = 'top.sheet.category'
    _description = 'HR Top Sheet Category'

    name = fields.Char('Top Sheet Category')


class HRCategory(models.Model):
    _name = 'hr.category'
    _description = 'HR Category'

    name = fields.Char('Category Name')
    employee_ids = fields.One2many('hr.employee', 'category_id', 'Employees')


class HREmployeeMedical(models.Model):
    _name = 'hr.employee.medical'
    _description = 'Employee Medical'

    disease = fields.Char('Disease', required=1)
    appointment_date = fields.Date('Appointment Date')
    discharge_date = fields.Date('Discharge Date')
    hospital = fields.Char('Hospital')
    employee_id = fields.Many2one('hr.employee', 'Employee')


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
    relationship = fields.Selection([('Father', 'Father'),
                                     ('Mother', 'Mother'),
                                     ('Son', 'Son'),
                                     ('Daughter', 'Daughter'),
                                     ('Wife', 'Wife')], string='Relationship')
    birthday = fields.Date('DOB')
    cnic = fields.Char('CNIC')
    phone_no = fields.Char('Contact No')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    status = fields.Selection([('Alive', 'Alive'),
                               ('Died', 'Died'),
                               ('Divorced', 'Divorced'),
                               ('Married', 'Married'),
                               ], string='Status')
    age_txt = fields.Char('Age', compute='_compute_age')
    age = fields.Integer('Age (Yearly)')
    jahez_fund = fields.Boolean('Jahez Fund', default=False)
    funeral_grant = fields.Boolean('Funeral Grant', default=False)

    # Eligible Criteria
    # For Son at age 26 and for daughter till Married
    eligibility_status = fields.Selection([('Eligible', 'Eligible'),
                                           ('Not Eligible', 'Not Eligible')
                                           ], string='Eligibility Status', compute='_compute_eligibility', store=True)

    def _compute_age(self):
        for rec in self:
            if rec.birthday:
                start = datetime.strptime(str(rec.birthday), OE_DFORMAT)
                end = datetime.strptime(str(time.strftime(OE_DFORMAT)), OE_DFORMAT)
                delta = end - start
                rec.age_txt = parse_date(delta)
            else:
                rec.age_txt = ''

    # This Function is used in the Cron Job monthly for Family Member Age Calculation
    @api.model
    def family_members_age_cron(self):
        today = date.today()
        members = self.env['hr.employee.family'].search([])
        if members:
            for member in members:
                if member.birthday:
                    age = today.year - member.birthday.year - ((today.month, today.day) < (member.birthday.month, member.birthday.day))
                    member.age = age
                else:
                    member.age = 0

    @api.depends('age', 'status', 'birthday', 'relationship')
    def _compute_eligibility(self):
        for rec in self:
            if rec.relationship=='Son':
                today = date.today()
                if rec.birthday:
                    age = today.year - rec.birthday.year - ((today.month, today.day) < (rec.birthday.month, rec.birthday.day))
                    rec.age = age
                else:
                    rec.age = 0
                if rec.age < 27:
                    rec.eligibility_status = 'Eligible'
                else:
                    rec.eligibility_status = 'Not Eligible'

            elif rec.relationship=='Daughter':
                if rec.status in ['Alive', 'Divorced']:
                    rec.eligibility_status = 'Eligible'
                else:
                    rec.eligibility_status = 'Not Eligible'

            elif rec.relationship=='Father':
                if rec.status=='Alive':
                    rec.eligibility_status = 'Eligible'
                else:
                    rec.eligibility_status = 'Not Eligible'

            elif rec.relationship=='Mother':
                if rec.status=='Alive':
                    rec.eligibility_status = 'Eligible'
                else:
                    rec.eligibility_status = 'Not Eligible'

            elif rec.relationship=='Wife':
                if rec.status not in ('Divorced', 'Died'):
                    rec.eligibility_status = 'Eligible'
                else:
                    rec.eligibility_status = 'Not Eligible'


class hr_experience(models.Model):
    _name = 'hr.experience'
    _description = 'HR Experience'

    def _total_experience_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                start = datetime.strptime(str(rec.start_date), OE_DFORMAT)
                end = datetime.strptime(str(rec.end_date), OE_DFORMAT)
                delta = end - start
                rec.total_experience = parse_date(delta)
            else:
                rec.total_experience = ''

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


class HREmployeeAcademic(models.Model):
    _name = 'hr.employee.academic'
    _description = 'Employee Academics'

    degree_level = fields.Selection([('under_matric', 'Under Matric'),
                                     ('matric', 'Matric'),
                                     ('inter', 'Intermediate'),
                                     ('undergraduate', 'Graduate'),
                                     ('postgraduate', 'Postgraduate'),
                                     ('professional_education', 'Professional Education'),
                                     ('mphil', 'MPhil'),
                                     ('phd', ' phd'),
                                     ], 'Degree Level', required=1)

    year = fields.Char('Passing Year')
    board = fields.Char('Board Name')
    subjects = fields.Char('Subjects')
    total_marks = fields.Float('Total Marks/CGPA', required=1)
    obtained_marks = fields.Float('Obtained Marks/CGPA', required=1)
    employee_id = fields.Many2one('hr.employee', 'Employee')
    degree_verified = fields.Boolean('Degree Verified', default=False)
    domicile = fields.Selection([('ICT', 'ICT'),
                                 ('Punjab', 'Punjab'),
                                 ('Sindh (U)', 'Sindh (U)'),
                                 ('Sindh (R)', 'Sindh (R)'),
                                 ('KPK', 'KPK'),
                                 ('Balochistan', 'Balochistan'),
                                 ('AJK', 'AJK'),
                                 ('GB', 'GB'),
                                 ], string='Domicile')


class HRBank(models.Model):
    _name = "hr.bank"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Banks"

    name = fields.Char('Bank Name', required=True, tracking=True)
    account = fields.Char('Account', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class HREmployeeDisabilityNature(models.Model):
    _name = 'hr.employee.disability.nature'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Disability Nature'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence', default=10)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    note = fields.Html('Note')

    _sql_constraints = [
        ('unique_name', 'unique(name)', "Name already exists for another Disability!"), ]

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        for rec in self:
            if rec.state!='draft':
                raise ValidationError(_('Only Draft entries can be deleted'))
        return super(HREmployeeDisabilityNature, self).unlink()


class HRReligion(models.Model):
    _name = 'hr.religion'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Employee Religion'

    name = fields.Char(string="Religion", required=True, tracking=True)
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    _sql_constraints = [
        ('unique_name', 'unique(name)', "Name already exists!"), ]

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You Cannot Delete the Record that are not in Draft State, Please contact the System Administrator.')
        return super(HRReligion, self).unlink()
