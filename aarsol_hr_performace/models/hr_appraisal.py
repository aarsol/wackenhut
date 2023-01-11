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


class AarPersonalTraits(models.Model):
    _name = "personal.traits"
    _description = "Faculty Personal Traits"
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
    name = fields.Char("Parameter")
    weightage = fields.Integer("Weightage")
    marks = fields.Integer("Marks")
    marks_obtained = fields.Integer("Marks Obtained")

    @api.model
    def create(self, vals):
        print("This wants to create", vals['appraisal_id'])
        appraisal = self.env['aar.appraisal.faculty'].sudo().search(
            [('id', '=', vals['appraisal_id'])])
        totalMarksObtained = 0
        for appraisal in appraisal.personal_trait_ids:
            totalMarksObtained = totalMarksObtained + appraisal.marks_obtained
        totalMarksObtained = int(totalMarksObtained) + int(vals['marks_obtained'])
        print("This will become the total marks Obtained", totalMarksObtained)
        update_value = {'aar_personal_trait_marks': totalMarksObtained}
        print("This is the update value", update_value)
        if int(totalMarksObtained) > 10:
            raise ValidationError(
                _('Total marks can not be greater than 10'))

        else:
            res = super(AarPersonalTraits, self).create(vals)
            # appraisal.update(update_value)
            return res


class AarTeaching(models.Model):
    _name = "aar.teaching"
    _description = "Student Teaching"
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
    name = fields.Char("Course Title")
    weightage = fields.Integer("Weightage")
    credits = fields.Integer("Credits")
    marks_obtained = fields.Integer("Marks Obtained")
    student_feedback_average = fields.Integer("Student Feedback Avg Percentage")
    class_audit = fields.Integer("Class Audit")

    @api.model
    def create(self, vals):
        appraisal = self.env['aar.appraisal.faculty'].sudo().search(
            [('id', '=', vals['appraisal_id'])])
        totalMarksObtained = 0
        for appraisal in appraisal.personal_trait_ids:
            totalMarksObtained = totalMarksObtained + appraisal.marks_obtained
        totalMarksObtained = int(totalMarksObtained) + int(vals['marks_obtained'])
        if int(totalMarksObtained) > 12:
            raise ValidationError(
                _('Total obtained marks can not be greater than 12'))
        elif int(vals['student_feedback_average']) > 100:
            raise ValidationError(
                _('Feedback percentage cannot be greater than 100'))
        elif int(vals['class_audit']) > 100:
            raise ValidationError(
                _('Class audit percentage cannot be greater than 100'))
        else:
            res = super(AarTeaching, self).create(vals)
            # appraisal.update(update_value)
            return res


class AarStudentSupervision(models.Model):
    _name = "aar.student.supervision"
    _description = "Student Supervision"
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
    name = fields.Char("Type")
    weightage = fields.Integer("Weightage")
    count = fields.Integer("Count")
    marks_obtained = fields.Integer("Marks Obtained")

    @api.model
    def create(self, vals):
        appraisal = self.env['aar.appraisal.faculty'].sudo().search(
            [('id', '=', vals['appraisal_id'])])
        totalMarksObtained = 0
        for appraisal in appraisal.aar_student_supervision_ids:
            totalMarksObtained = totalMarksObtained + appraisal.marks_obtained
        totalMarksObtained = int(totalMarksObtained) + int(vals['marks_obtained'])
        print("This will become the total marks Obtained", totalMarksObtained)
        update_value = {'aar_personal_trait_marks': totalMarksObtained}
        print("This is the update value", update_value)
        if int(totalMarksObtained) > 10:
            raise ValidationError(
                _('Total obtained marks can not be greater than 10'))
        else:
            res = super(AarStudentSupervision, self).create(vals)
            # appraisal.update(update_value)
            return res


class AarResearchPublications(models.Model):
    _name = "aar.research.publications"
    _description = "Research Publications"
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
    name = fields.Char("Type")
    weightage = fields.Integer("Weightage")
    count = fields.Integer("Count")
    total_marks = fields.Integer("Total Marks")

    @api.model
    def create(self, vals):
        appraisal = self.env['aar.appraisal.faculty'].sudo().search(
            [('id', '=', vals['appraisal_id'])])
        totalMarksObtained = 0
        for appraisal in appraisal.publication_ids:
            totalMarksObtained = totalMarksObtained + appraisal.total_marks
        totalMarksObtained = int(totalMarksObtained) + int(vals['total_marks'])
        print("This will become the total marks Obtained", totalMarksObtained)
        update_value = {'aar_personal_trait_marks': totalMarksObtained}
        print("This is the update value", update_value)
        if int(totalMarksObtained) > 20:
            raise ValidationError(
                _('Total obtained marks can not be greater than 20'))
        else:
            res = super(AarResearchPublications, self).create(vals)
            # appraisal.update(update_value)
            return res


class AarFundingActivities(models.Model):
    _name = "aar.funding.activities"
    _description = "FUNDING & ENTREPRENEURIAL ACTIVITIES"
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
    name = fields.Char("Type")
    amount = fields.Integer("Amount")
    point = fields.Integer("Point")
    marks_obtained = fields.Integer("Marks Obtained")

    # @api.model
    # def create(self, vals):
    #     appraisal = self.env['aar.appraisal.faculty'].sudo().search(
    #         [('id', '=', vals['appraisal_id'])])
    #     totalMarksObtained = 0
    #     for appraisal in appraisal.aar_funding_activity_ids:
    #         totalMarksObtained = totalMarksObtained + appraisal.marks_obtained
    #     totalMarksObtained = int(totalMarksObtained) + int(vals['marks_obtained'])
    #     if int(totalMarksObtained) > 20:
    #         raise ValidationError(
    #             _('Total obtained marks can not be greater than 20'))
    #     else:
    #         print("This is the vals in aar.funding.activities ",vals)
    #         res = super(AarResearchPublications, self).create(vals)
    #         # appraisal.update(update_value)
    #         return res


class AarInstitutionalServices(models.Model):
    _name = "aar.institutional.services"
    _description = "Institutional Services"
    appraisal_id = fields.Many2one("aar.appraisal.faculty", "Associated Assessment")
    name = fields.Char("Type")
    weightage = fields.Integer("Weightage")
    count = fields.Integer("Count")
    marks_obtained = fields.Integer("Marks Obtained")

    # @api.model
    # def create(self, vals):
    #     appraisal = self.env['aar.appraisal.faculty'].sudo().search(
    #         [('id', '=', vals['appraisal_id'])])
    #     totalMarksObtained = 0
    #     for appraisal in appraisal.aar_institutional_services_ids:
    #         totalMarksObtained = totalMarksObtained + appraisal.marks_obtained
    #     totalMarksObtained = int(totalMarksObtained) + int(vals['marks_obtained'])
    #     if int(totalMarksObtained) > 20:
    #         raise ValidationError(
    #             _('Total obtained marks can not be greater than 20'))
    #     else:
    #         res = super(AarInstitutionalServices, self).create(vals)
    #         # appraisal.update(update_value)
    #         return res


class AarAppraisalFaculty(models.Model):
    _name = 'aar.appraisal.faculty'
    _description = "AAR Appraisal Faculty"

    name = fields.Char("Appraisal Form Name")
    state = fields.Selection(
        [('draft', 'Draft'), ('reporting', 'Marked to Reporting Officer'),
         ('counter-sign', 'Marked to Counter-Sign Officer'),
         ('senior-counter-sign', 'Marked to Senior Counter-Sign Officer'),
         ('senior-counter-sign-2', 'Marked to Director Estab.'),
         ('senior-counter-sign-3', 'Marked to Rector'),
         ],
        string='Appraisal State',
        default='draft', tracking=True)
    active = fields.Boolean(string="Active", default=True)
    employee_id = fields.Many2one("hr.employee", string="Appraisal Employee")
    reporting_id = fields.Many2one(string="Reporting Officer", related="employee_id.parent_id")
    counter_sign_id = fields.Many2one(string="Counter Sign Officer", related="employee_id.counter_sign_id")
    senior_counter_sign_id = fields.Many2one(string="Senior Counter Sign Officer",
                                             related="employee_id.senior_counter_sign_id")

    payscale = fields.Char(string="Payscale", related="employee_id.payscale_id.name")
    joining_date = fields.Date(string="Joining Date", related="employee_id.joining_date")
    designation = fields.Char(string="Designation", related="employee_id.job_id.name")
    phone = fields.Char(string="Phone", related="employee_id.phone")
    email = fields.Char(string="Phone", related="employee_id.work_email")
    qualification = fields.Char(string="Qualification", related="employee_id.qualification")
    specialization = fields.Char(string="Specialization", related="employee_id.specialization")
    citations = fields.Integer(string="Citations", related="employee_id.citations")
    h_index = fields.Integer(string="H Index", related="employee_id.h_index")
    focus_area = fields.Char(string="Focus Area", related="employee_id.focus_area")

    start_date = fields.Date(string="Appraisal Starting Date")
    end_date = fields.Date(string="Appraisal Ending Date")
    birthday = fields.Date(string="Joining Date", related="employee_id.birthday")

    courses_taught_ids = fields.One2many('assess.courses.taught', 'appraisal_id', string="Courses Taught")
    student_supervision_ids = fields.One2many('assess.student.supervision', 'appraisal_id',
                                              string="Students Supervised")
    research_publication_ids = fields.One2many('assess.research.publication', 'appraisal_id',
                                               string="Research Publications")
    funding_activities_ids = fields.One2many('assess.funding.activities', 'appraisal_id',
                                             string="Funding Activities")
    institutional_services_ids = fields.One2many('assess.institutional.services', 'appraisal_id',
                                                 string="Institutional Services")

    # to be filled by reporting officer
    personal_trait_ids = fields.One2many('personal.traits', 'appraisal_id', string="Personality Traits")
    aar_student_supervision_ids = fields.One2many('aar.student.supervision', 'appraisal_id',
                                                  string="Student Supervision")
    publication_ids = fields.One2many("aar.research.publications", 'appraisal_id', string="Publication Survey")
    aar_funding_activity_ids = fields.One2many("aar.funding.activities", 'appraisal_id', "Funding Activities Survey")
    aar_institutional_services_ids = fields.One2many("aar.institutional.services", 'appraisal_id',
                                                     "Institutional Services Survey")
    aar_teaching_ids = fields.One2many("aar.teaching", 'appraisal_id', "Teaching Record Survey")

    aar_personal_trait_marks = fields.Integer(string="Personal Trait Marks", compute="calculate_all_total_marks")
    aar_teaching_marks = fields.Float(string="Aar Teaching Marks")
    aar_publication_marks = fields.Integer(string="Aar Publication Marks")
    aar_student_supervision_marks = fields.Integer(string="Aar Student Supervision Marks")
    aar_funding_activity_marks = fields.Integer(string="Aar Funding Activity Marks")
    aar_institutional_marks = fields.Integer(string="Aar Institutional Marks")
    aar_total_marks = fields.Float(string="Aar Total Marks")
    overall_grade = fields.Char(string="Overall Grade")

    signing_authority_remarks = fields.Text(string="Comments / Recommendations by the Reporting Officer")
    signing_degree_of_contact = fields.Selection(
        [('weak', 'Weak'), ('fair', 'Fair'),
         ('strong', 'Strong')],
        string='Degree Of Contact',
        default='weak', tracking=True)
    counter_sign_remarks = fields.Text(string="Comments / Recommendations by the Countersigning Officer")
    senior_counter_sign_remarks = fields.Text(string="Comments / Recommendations by the Senior Countersigning Officer")
    senior_counter_sign_recommendation = fields.Selection(
        [('lenient', 'Lenient'), ('fair', 'Fair'),
         ('strict', 'Strict')],
        string='Degree Of Contact',
        default='lenient', tracking=True)

    def calculate_all_total_marks(self):
        for rec in self:
            personal_trait_obtained = 0
            aar_teaching_obtained = 0
            teaching_student_feedback = 0
            teaching_class_audit = 0

            student_supervision_obtained = 0

            aar_publications_obtained = 0

            fuding_activity_marks_obtained = 0

            aar_institutional_services_obtained = 0

            for personal_trait in rec.personal_trait_ids:
                personal_trait_obtained = personal_trait_obtained + personal_trait.marks_obtained
            rec.aar_personal_trait_marks = personal_trait_obtained

            for student_supervision in rec.aar_student_supervision_ids:
                student_supervision_obtained = student_supervision_obtained + student_supervision.marks_obtained
            rec.aar_student_supervision_marks = student_supervision_obtained

            for aar_publication in rec.publication_ids:
                aar_publications_obtained = aar_publications_obtained + aar_publication.total_marks
            rec.aar_publication_marks = aar_publications_obtained

            for aar_funding_activity in rec.aar_funding_activity_ids:
                fuding_activity_marks_obtained = fuding_activity_marks_obtained + aar_funding_activity.marks_obtained
            rec.aar_funding_activity_marks = fuding_activity_marks_obtained

            for aar_institutional_service in rec.aar_institutional_services_ids:
                aar_institutional_services_obtained = aar_institutional_services_obtained + aar_institutional_service.marks_obtained
            rec.aar_institutional_marks = aar_institutional_services_obtained

            for aar_teaching in rec.aar_teaching_ids:
                aar_teaching_obtained = aar_teaching_obtained + aar_teaching.marks_obtained
                teaching_student_feedback = teaching_student_feedback + aar_teaching.student_feedback_average
                teaching_class_audit = teaching_class_audit + aar_teaching.class_audit

            # calculating the mean average
            teaching_class_audit = 0
            teaching_student_feedback = 0
            if len(rec.aar_teaching_ids) > 0:
                teaching_class_audit = teaching_class_audit / len(rec.aar_teaching_ids)
                teaching_student_feedback = teaching_student_feedback / len(rec.aar_teaching_ids)

            # dividing 100 and multiplying by 5 and 3 (for audit) respectively accoding to given formula
            teaching_class_audit = teaching_class_audit * 0.03
            teaching_student_feedback = teaching_student_feedback * 0.05
            print("These are teaching marks")
            rec.aar_teaching_marks = aar_teaching_obtained + teaching_class_audit + teaching_student_feedback

            total_marks = rec.aar_personal_trait_marks + round(rec.aar_teaching_marks,
                                                               2) + rec.aar_publication_marks + rec.aar_student_supervision_marks + rec.aar_funding_activity_marks + rec.aar_institutional_marks

            if total_marks >= 90:
                rec.overall_grade = "Excellent"
            if total_marks < 90:
                rec.overall_grade = "Very Good"
            if total_marks < 80:
                rec.overall_grade = "Good"
            if total_marks < 70:
                rec.overall_grade = "Average"
            if total_marks < 60:
                rec.overall_grade = "Low Average"
            if total_marks < 50:
                rec.overall_grade = "Poor"

            rec.aar_total_marks = round(total_marks, 2)


class AarAppraisalEmployee(models.Model):
    _name = "aar.appraisal.employee"
    _description = 'Aar Appraisal Non Faculty'

    name = fields.Char("Appraisal Form Name")
    employee_id = fields.Many2one("hr.employee", string="Appraisal Employee")
    reporting_id = fields.Many2one(string="Reporting Officer", related="employee_id.parent_id")
    counter_sign_id = fields.Many2one(string="Counter Sign Officer", related="employee_id.counter_sign_id")
    senior_counter_sign_id = fields.Many2one(string="Senior Counter Sign Officer",
                                             related="employee_id.senior_counter_sign_id")
    senior_counter_sign_id_two = fields.Many2one(string="Senior Counter Sign Officer Two",
                                             related="employee_id.senior_counter_sign_id_two")
    senior_counter_sign_id_three = fields.Many2one(string="Senior Counter Sign Officer Three",
                                                 related="employee_id.senior_counter_sign_id_three")
    payscale = fields.Char(string="Payscale", related="employee_id.payscale_id.name")
    joining_date = fields.Date(string="Joining Date", related="employee_id.joining_date")
    start_date = fields.Date(string="Appraisal Starting Date")
    end_date = fields.Date(string="Appraisal Ending Date")
    birthday = fields.Date(string="Joining Date", related="employee_id.birthday")

    # state = fields.Selection(
    #     [('draft', 'Draft'), ('active', 'Active')],
    #     string='Status',
    #     default='draft', tracking=True)
    active = fields.Boolean(string="Active", default=True)
    participation_ids = fields.One2many('aar.participation', 'appraisal_id', string="Conference Participations")
    committee_membership_ids = fields.One2many('aar.committee.membership', 'appraisal_id',
                                               string="Conference Participations")
    post_description = fields.Text("Post Description")
    additional_duties = fields.Text("Additional Duties")
    achievements = fields.Text("Significant Achievements")
    section_ids = fields.One2many('aar.section', 'appraisal_id', string="Sections")
    reporting_observations = fields.Text("Observations By Reporting Officer")
    signing_degree_of_contact = fields.Selection(
        [('weak', 'Weak'), ('fair', 'Fair'),
         ('strong', 'Strong')],
        string='Degree Of Contact',
        default='weak', tracking=True)
    percentage_marks = fields.Integer("Percentage Marks")
    marks_grading = fields.Char(string="Overall Grading")
    counter_sign_observations = fields.Text("Observations By Counter Sign Officer")
    senior_counter_sign_remarks = fields.Text(string="Comments / Recommendations by the Senior Countersigning Officer")
    senior_counter_sign_recommendation = fields.Selection(
        [('lenient', 'Lenient'), ('fair', 'Fair'),
         ('strict', 'Strict')],
        string='Senior Counter Sign Recommendation',
        default='lenient', tracking=True)

    grandTotalMarks = fields.Integer("Total Marks of sections",default=0)
    totalObtainedMarks = fields.Integer("Total Marks Obtained",default=0)
    evaluation_quality = fields.Selection(
        [('exaggerated', 'Exaggerated'), ('fair', 'Fair'), ('biased', 'Biased')],
        string='Evaluation Quality',
        default='fair', tracking=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('reporting', 'Marked to Reporting Officer'),
         ('counter-sign', 'Marked to Counter-Sign Officer'),
         ('senior-counter-sign', 'Marked to Senior Counter-Sign Officer'),
         ('senior-counter-sign-2', 'Marked to Director Estab.'),
         ('senior-counter-sign-3', 'Marked to Rector'),
         ('approved', 'Approved'),
         ],
        string='Appraisal State',
        default='draft', tracking=True)

    # # @api.onchange("section_ids")
    # def on_change_section_id(self):
    #     for rec in self:
    #         grandTotal = 0
    #         grandTotalObtained = 0
    #         percentage = 0
    #         for section in rec.section_ids:
    #             print("section.appraisal_id.id", section.appraisal_id.id)
    #             if section.appraisal_id.id == rec.id:
    #                 # print("section",section)
    #                 grandTotal = grandTotal + section.totalMarks
    #                 grandTotalObtained = grandTotalObtained + section.marks
    #         if grandTotal > 50:
    #             raise ValidationError(_("Total marks of section questions cannot be greater than 50"))
    #
    #         if grandTotal != 0:
    #             percentage = int(grandTotalObtained) / int(grandTotal) * 100
    #             percentage = percentage / 2
    #             rec.percentage_marks = (int(grandTotalObtained) / int(grandTotal) * 100) / 2
    #         if percentage <= 20:
    #             rec.marks_grading = "Below Average"
    #         elif percentage > 20 and percentage <= 30:
    #             rec.marks_grading = "Average"
    #         elif percentage > 30 and percentage <= 40:
    #             rec.marks_grading = "Good"
    #         elif percentage > 40 and percentage <= 50:
    #             rec.marks_grading = "Excellent"
    #         rec.totalObtainedMarks = grandTotalObtained
    #         rec.grandTotalMarks = grandTotal


class AarParticipation(models.Model):
    _name = "aar.participation"
    _description = "Participation in Conference , Seminars"

    name = fields.Char("Title")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    duration = fields.Float("Duration in Days", compute='_total_duration', default=0, digits=(16, 2))
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    appraisal_id = fields.Many2one("aar.appraisal.employee", "Associated Appraisal")

    @api.depends('start_date', 'end_date')
    def _total_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date < rec.end_date:
                st = datetime.strptime(str(rec.end_date), "%Y-%m-%d")
                en = datetime.strptime(str(rec.start_date), "%Y-%m-%d")
                rec.duration = float((st - en).days)
            else:
                rec.duration = 0


class AarCommitteeMembership(models.Model):
    _name = 'aar.committee.membership'
    _description = "Committee Whom Employee is Member"

    name = fields.Char("Name of Committee")
    meetings_held = fields.Integer("Meetings Held")
    meetings_attended = fields.Integer("Meetings Attended")
    reason = fields.Text("Reason for not attending meetings")
    appraisal_id = fields.Many2one("aar.appraisal.employee", "Associated Appraisal")


class AarSections(models.Model):
    _name = "aar.section"
    _description = "Main Sections Sections"

    name = fields.Char("Section Name")
    selected_name = fields.Char("Selected Section Name")
    selected_marks = fields.Integer("Selected Question Marks")
    appraisal_id = fields.Many2one("aar.appraisal.employee", "Associated Section")
    section_question_ids = fields.One2many('aar.section.question', 'section_id',
                                           string="Section Questions", ondelete="cascade")

class AarSectionsAppraisal(models.Model):
    _name = "aar.section.appraisal"
    _description = "Sections for Appraisal"
    name = fields.Char("Section Name")
    selected_name = fields.Char("Selected Section Name")
    selected_marks = fields.Integer("Selected Question Marks")
    appraisal_id = fields.Many2one("aar.appraisal.employee", "Associated Section")
    section_question_ids = fields.One2many('aar.section.question', 'section_id',
                                           string="Section Questions", ondelete="cascade")

class AarSectionQuestions(models.Model):
    _name = "aar.section.question.appraisal"
    _description = "Questions For Sections"

    name = fields.Char("Question Text")
    marks = fields.Integer("Obtained Marks")
    selected = fields.Boolean("Selected")
    section_id = fields.Many2one("aar.section", "Associated Section")

class AarSectionQuestions(models.Model):
    _name = "aar.section.question"
    _description = "Questions For Sections"

    name = fields.Char("Question Text")
    marks = fields.Integer("Obtained Marks")
    totalMarks = fields.Integer("Total Marks", default=5)
    section_id = fields.Many2one("aar.section", "Associated Section")


    # @api.onchange('marks')
    # def validate_marks(self):
    #     if self.marks > 5:
    #         raise ValidationError(
    #             _('Marks can not be greater than 5'))

    # @api.model
    # def create(self, values):
    #     record = super(res_partner, self).create(values)


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    # faculty_appraisal_id = fields.Many2one('aar.appraisal.faculty', string="Faculty Appraisal")
    # employee_appraisal_id = fields.Many2one('aar.appraisal.employee', string="Non Faculty Appraisal")
    counter_sign_id = fields.Many2one('hr.employee', string="Counter Sign By", groups="hr.group_hr_user")
    senior_counter_sign_id = fields.Many2one('hr.employee', string="Senior Counter Sign By",groups="hr.group_hr_user")
    senior_counter_sign_id_two = fields.Many2one('hr.employee', string="Senior Counter Sign By Two",groups="hr.group_hr_user")
    senior_counter_sign_id_three = fields.Many2one('hr.employee', string="Senior Counter Sign By Three",groups="hr.group_hr_user")
    allow_initiation = fields.Boolean(string="Allow Appraisal Initiation", default=False,groups="hr.group_hr_user")
    employee_type = fields.Selection(selection_add=[('faculty', 'Faculty'),
                                                    ('support', 'Support Staff')
                                                    ], string='Faculty Type', index=True, groups="hr.group_hr_user")

    qualification = fields.Char(string="Qualification",groups="hr.group_hr_user")
    specialization = fields.Char(string="Specialization",groups="hr.group_hr_user")
    citations = fields.Integer(string="Citations",groups="hr.group_hr_user")
    h_index = fields.Integer(string="H Index",groups="hr.group_hr_user")
    focus_area = fields.Char(string="Focus Area",groups="hr.group_hr_user")

    def action_send_survey(self):
        print("This is the partner id ", self.parent_id.user_id.partner_id.id)

        """ Open a window to compose an email, pre-filled with the survey message """
        # Ensure that this survey has at least one question.
        if not self.survey_id.question_ids:
            raise UserError(_('You cannot send an invitation for a survey that has no questions.'))

        # Ensure that this survey has at least one section with question(s), if question layout is 'One page per section'.
        if self.survey_id.questions_layout == 'page_per_section':
            if not self.survey_id.page_ids:
                raise UserError(
                    _('You cannot send an invitation for a "One page per section" survey if the survey has no sections.'))
            if not self.survey_id.page_ids.mapped('question_ids'):
                raise UserError(
                    _('You cannot send an invitation for a "One page per section" survey if the survey only contains empty sections.'))

        if self.survey_id.state == 'closed':
            raise exceptions.UserError(_("You cannot send invitations for closed surveys."))

        template = self.env.ref('survey.mail_template_user_input_invite', raise_if_not_found=False)

        local_context = dict(
            self.env.context,
            default_survey_id=self.survey_id.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            notif_layout='mail.mail_notification_light',
            default_partner_ids=[4, self.parent_id.user_id.partner_id.id]
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'survey.invite',
            'target': 'new',
            'context': local_context,
        }
