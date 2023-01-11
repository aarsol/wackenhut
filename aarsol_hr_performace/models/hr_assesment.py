from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import time
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
import logging
import math
import re

_logger = logging.getLogger(__name__)
import pdb


class AarPersonalAssessment(models.Model):
    _name = 'aar.assessment'

    name = fields.Char("Assessment Name")
    courses_taught_ids = fields.Char("Assessment Name")
    student_supervision_ids = fields.Char("Assessment Name")
    research_publication_ids = fields.Char("Assessment Name")
    funding_activities_ids = fields.Char("Assessment Name")
    institutional_services_ids = fields.Char("Assessment Name")
    # courses_taught_ids = fields.One2many('assess.courses.taught', 'appraisal_id', string="Courses Taught")
    # student_supervision_ids = fields.One2many('assess.student.supervision', 'appraisal_id',
    #                                           string="Students Supervised")
    # research_publication_ids = fields.One2many('assess.research.publication', 'appraisal_id',
    #                                           string="Research Publications")
    # funding_activities_ids = fields.One2many('assess.funding.activities', 'appraisal_id',
    #                                            string="Funding Activities")
    # institutional_services_ids = fields.One2many('assess.institutional.services', 'appraisal_id',
    #                                            string="Institutional Services")





class AarPersonalAssessment(models.Model):
    _name = "assess.courses.taught"
    _description = "Courses Taught"

    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
    name = fields.Char("Name")
    code = fields.Char("Code")
    batch = fields.Char("Batch")
    semester = fields.Char("Semester")
    credits = fields.Char("Credits")
    student_feedback = fields.Char("Student Feedback")
    class_audit = fields.Char("Class Audit")


class AssessStudentSupervision(models.Model):
    _name = 'assess.student.supervision'
    _description = "Student Supervised"

    name = fields.Char("Student Name")
    reg_num = fields.Char("Register Number")
    batch = fields.Char("Student Batch")
    semester = fields.Char("Student Semester")
    type = fields.Selection(
        [('phd', 'Phd Thesis'), ('ms', 'Ms Thesis'), ('fyp', 'Final Year Project'), ('internship', 'Internship')],
        string='Type',
        default='fyp', tracking=True)
    topic = fields.Char("Topic")
    keywords = fields.Char("Key Words")

    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")


class AssessResearchPublication(models.Model):
    _name = "assess.research.publication"
    _description = "Assessment Research Publications"

    name = fields.Char("Title of Paper")
    reg_num = fields.Char("PISSN No./EISSN No/Registration No.")
    published_in = fields.Char("Published In")
    author_name = fields.Char("Name Of Author")
    co_author_name = fields.Char("Co Author Name")
    organizer = fields.Char("Organizer")
    issue_number = fields.Char("Issue Number")
    vol_number = fields.Char("Volume Number")
    published_pages = fields.Char("Published Papers")
    publication_date = fields.Date(string="Publication Date")
    keyword = fields.Char("Keyword")
    url = fields.Char("URL for the Paper")
    impact_factor = fields.Char("Impact Factor")
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")

    type = fields.Selection(
        [('patent', 'Patent'), ('journal', 'Journal'), ('book', 'Book'), ('chapter', 'Chapter'),
         ('conference', 'Conference')],
        string='Type',
        default='patent', tracking=True)
    level = fields.Selection(
        [('international', 'International'), ('local', 'Local')],
        string='Level',
        default='international', tracking=True)
    rank = fields.Selection(
        [('q1', 'Q1 Rank'), ('q2', 'Q2 Rank'), ('w', 'W Category'), ('x', 'X Category'),
         ('y', 'Y Category'), ('other', 'Other')],
        string='rank',
        default='q1', tracking=True)
    index = fields.Selection(
        [('isi', 'ISI'), ('scopus', 'Scopus'), ('hec', 'HEC')],
        string='Index',
        default='isi', tracking=True)


class AssessFundingActivities(models.Model):
    _name = "assess.funding.activities"
    _description = "Assessment Funding Activities"

    type = fields.Selection(
        [('industrial', 'Industrial Project'), ('rnd', 'R&D Project'), ('consultancy', 'Consultancy'),
         ('startup', 'Start-Up'),
         ('other', 'Other')],
        string='Type',
        default='industrial', tracking=True)
    level = fields.Selection(
        [('international', 'International'), ('local', 'Local')],
        string='Level',
        default='international', tracking=True)
    approval_date = fields.Date(string="Date of Approval")
    name = fields.Char("Title")
    amount = fields.Char("Amount")
    keywords = fields.Char("Keywords")
    copi = fields.Char("Co-Pi")
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")


class AssessInstitutionalServices(models.Model):
    _name = "assess.institutional.services"
    _description = "Assessment Institutional Services"
    _rec_name = "type"

    type = fields.Selection(
        [('hod', 'HOD/Chairman'), ('c-governor', 'Committee Covernor'), ('c-member', 'Committee Member'),
         ('student_advisory', 'Student Advisory'), ('co_supervision', 'Co Supervision'),
         ('co-pi', 'Co-Pi')],
        string='Type',
        default='industrial', tracking=True)
    frequency = fields.Selection(
        [('regular', 'Regular'), ('semester-wise', 'Semester Wise'), ('monthly', 'Monthly'), ('weekly', 'Weekly'),
         ('daily', 'Daily')],
        string='Level',
        default='international', tracking=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    keywords = fields.Char("Keywords")
    description = fields.Text("Description")
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
