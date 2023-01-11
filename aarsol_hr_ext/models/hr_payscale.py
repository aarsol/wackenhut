from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
import logging

_logger = logging.getLogger(__name__)


class HRPayScaleCategory(models.Model):
    _name = 'hr.payscale.category'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'HR PayScale Category'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code', tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    date_start = fields.Date('Start Date', tracking=True)
    date_end = fields.Date('End Date', tracking=True)
    active = fields.Boolean('Active', tracking=True)
    scale_ids = fields.One2many('hr.payscale', 'scale_category_id', 'Scale(s)')
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    employee_summary = fields.Html('Employee Summary', compute='_compute_employee_summary')

    @api.constrains('date_start', 'date_end')
    def date_period_constrains(self):
        for rec in self:
            if rec.date_end and rec.date_start and rec.date_start > rec.date_end:
                raise ValidationError(_('Date Start should be Before Date End'))

    def action_lock(self):
        self.state = 'lock'
        if self.scale_ids:
            self.scale_ids.write({'state': 'lock'})

    def action_unlock(self):
        self.state = 'draft'
        if self.scale_ids:
            self.scale_ids.write({'state': 'draft'})

    def _compute_employee_summary(self):
        for rec in self:
            total_employee = 0
            employee_detail = ''
            if rec.scale_ids:
                employee_detail = """
                          <table class="table">
                              <tbody>
                                  <tr style="text-align:left;font-size:15;background-color: #17134e;color: white;">
                                     <th>Sr#.</th>
                                     <th>Payscale</th>
                                     <th>Active Employee(s)</th>
                                 </tr>
                      """
                sr = 1
                for payscale in rec.scale_ids:
                    employee_count = self.env['hr.employee'].search_count([('payscale_category', '=', rec.id),
                                                                           ('payscale_id', '=', payscale.id),
                                                                           ('state', '=', 'active')])
                    total_employee += employee_count
                    if employee_count==0:
                        employee_detail += """
                                  <tr style="text-left:center;font-size:20;background-color: #ffc1cc;">
                                      <td>%s</td>
                                      <td>%s</td>
                                      <td>%s</td>
                                  </tr>
                              """ % (sr, payscale.name, employee_count)
                    else:
                        employee_detail += """
                                     <tr style="text-left:center;font-size:20;background-color: #FEF9E7;">
                                         <td>%s</td>
                                         <td>%s</td>
                                         <td>%s</td>
                                     </tr>
                                 """ % (sr, payscale.name, employee_count)
                    sr += 1
                employee_detail += """ 
                          <tr style="text-align:left;font-size:20;font-weight:bold;background-color: #17134e;color: white;">
                              <td></td>
                              <td></td>
                              <td>%s</td>
                          </tr>
                          </tbody>
                          </table> """ % total_employee
            rec.employee_summary = employee_detail


class HRPayScale(models.Model):
    _name = 'hr.payscale'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'HR PayScale'

    name = fields.Char('Grade', tracking=True)
    code = fields.Char('Code', tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    basic_pay = fields.Float('Basic Pay', tracking=True)
    increment = fields.Float('Per Stage Increment', tracking=True)
    stages = fields.Integer('Stages', tracking=True)
    last_limit = fields.Float('Last Limit', tracking=True)
    scale_category_id = fields.Many2one('hr.payscale.category', 'Category', tracking=True)
    active = fields.Boolean('Active', related='scale_category_id.active')
    employee_ids = fields.One2many('hr.employee', 'payscale_id', 'Employee(s)')
    date_start = fields.Date('Start Date', tracking=True, related='scale_category_id.date_start', store=True)
    date_end = fields.Date('End Date', tracking=True, related='scale_category_id.date_end', store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    employee_summary = fields.Html('Employee Summary', compute='_compute_employee_summary')

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    def _compute_employee_summary(self):
        for rec in self:
            total_employee = 0
            employee_detail = ''
            employee_detail = """
                         <table class="table">
                             <tbody>
                                 <tr style="text-align:left;font-size:15;background-color: #17134e;color: white;">
                                    <th>Sr#.</th>
                                    <th>Stage</th>
                                    <th>Active Employee(s)</th>
                                </tr>
                     """
            sr = 1
            for n in range(rec.stages + 1):
                employee_count = self.env['hr.employee'].search_count([('payscale_id', '=', rec.id),
                                                                       ('stage', '=', n),
                                                                       ('state', '=', 'active')])
                total_employee += employee_count
                if employee_count==0:
                    employee_detail += """
                                 <tr style="text-left:center;font-size:20;background-color: #ffc1cc;">
                                     <td>%s</td>
                                     <td>%s</td>
                                     <td>%s</td>
                                 </tr>
                             """ % (sr, str(n), employee_count)
                else:
                    employee_detail += """
                                 <tr style="text-left:center;font-size:20;background-color: #FEF9E7;">
                                     <td>%s</td>
                                     <td>%s</td>
                                     <td>%s</td>
                                 </tr>
                             """ % (sr, str(n), employee_count)
                sr += 1
            employee_detail += """ 
                         <tr style="text-align:left;font-size:20;font-weight:bold;background-color: #17134e;color: white;">
                             <td></td>
                             <td></td>
                             <td>%s</td>
                         </tr>
                         </tbody>
                             </table> """ % total_employee
            rec.employee_summary = employee_detail


class HRGradeChange(models.Model):
    _name = "hr.grade.change"
    _description = 'HR Employee Grade Change'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    READONLY_STATES = {
        'part_approved': [('readonly', True)],
        'approved': [('readonly', True)],
        'rejected': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    date = fields.Date('Entry Date', tracking=True)
    description = fields.Text('Description')
    old_contract_end_date = fields.Date('Prev. Contract End Date', help="Previous Contract End Date.", tracking=True)
    new_contract_start_date = fields.Date('New Contract Start Date', help="New Contract Start Date.", tracking=True)
    salary_start_date = fields.Date('Salary Start Date', default=fields.Date.today())
    type = fields.Selection([('increment', 'Increment'),
                             ('promotion', 'Promotion'),
                             ('Demotion', 'Demotion')
                             ], string='Type', tracking=True, index=True, default='increment')
    promotion_type = fields.Selection([('active_promotion', 'Acting Promotion'),
                                       ('regular_promotion', 'Regular Promotion'),
                                       ], default='regular_promotion', string='Promotion Type', index=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancel')
                              ], default='draft', string='State', tracking=True, index=True)
    line_ids = fields.One2many('hr.grade.change.line', 'grade_change_id', string='Lines')
    total_records = fields.Integer('Total', compute='_compute_total_records', store=True)
    grade_change_summary = fields.Html('Grade Change Summary', compute='_compute_grade_change_summary')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New'))==_('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.grade.change') or _('New')
        result = super().create(vals)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError(_('Only Draft Entries can be delete.'))
            if rec.line_ids:
                rec.line_ids.unlink()
        return super(HRGradeChange, self).unlink()

    def action_approve(self):
        for line in self.line_ids:
            if not line.no_action:
                if line.new_grade.id==line.grade.id and line.new_stage==line.stage and line.personal_pay_count==line.employee_id.personal_pay_count:
                    raise UserError(_('Employee %s have same new payscale %s as its previous %s') % (line.employee_id.name, line.new_grade.name, line.grade.name))

                # Close Previous Contract
                old_contract = self.close_contract(line.employee_id)
                line.employee_id.write({'payscale_id': line.new_grade.id,
                                        'stage': line.new_stage,
                                        'personal_pay_count': line.personal_pay_count})
                # Create New Contract
                self.create_contract(line.employee_id, line, old_contract)
            else:
                line.remarks = 'Penalty Issue'
        self.state = 'approve'

    def action_approve2(self):
        for line in self.line_ids:
            if not line.no_action:
                if line.new_grade.id==line.grade.id and line.new_stage==line.stage and line.personal_pay_count==line.employee_id.personal_pay_count:
                    raise UserError(_('Employee %s have same new payscale %s as its previous %s') % (line.employee_id.name, line.new_grade.name, line.grade.name))

                # Close Previous Contract
                old_contract = self.close_contract(line.employee_id)
                line.employee_id.write({'payscale_id': line.new_grade.id,
                                        'stage': line.new_stage,
                                        'personal_pay_count': line.personal_pay_count,
                                        'department_id': line.department_id and line.department_id.id or False,
                                        'job_id': line.job_id and line.job_id.id or False})
                # Create New Contract
                self.create_contract(line.employee_id, line, old_contract)
            else:
                line.remarks = 'Penalty Issue'
        self.state = 'approve'

    def close_contract(self, employee):
        old_contract = False
        old_contract = self.env['hr.contract'].search([('employee_id', '=', employee.id),
                                                       ('state', '=', 'open')])
        if old_contract:
            if old_contract.allowance_ids:
                for alw in old_contract.allowance_ids:
                    alw.expired = True
            if old_contract.deduction_ids:
                for deduct in old_contract.deduction_ids:
                    deduct.expired = True
            if self.old_contract_end_date:
                old_contract.date_end = self.old_contract_end_date
            old_contract.state = 'close'
        return old_contract

    def create_contract(self, employee, line, old_contract):
        new_contract = False
        personal_pay_amount = 0
        if old_contract:
            contracts = self.env['hr.contract'].search_count([('employee_id', '=', line.employee_id.id)])
            contracts += 1
            contract_name = 'EM.' + str(line.employee_id.code) + '-' + str(contracts)

            wage = line.new_grade.basic_pay + (line.new_grade.increment * line.new_stage)
            if line.personal_pay_count > 0:
                line.employee_id.personal_pay_count = line.personal_pay_count
                personal_pay_amount = line.personal_pay_count * line.new_grade.increment
            new_contract = old_contract.copy(
                default={
                    'name': contract_name,
                    'state': 'draft',
                    'date_start': self.new_contract_start_date,
                    'new_date_start': self.salary_start_date,
                    'date_end': False,
                    'wage': wage,
                    'personal_pay_amount': personal_pay_amount,
                    'allowance_ids': [],
                    'deduction_ids': [],
                }
            )

            # if old_contract.allowance_ids:
            #     for alw in old_contract.allowance_ids:
            #         allow_vals = ({
            #             'contract_id': new_contract.id,
            #             'employee_id': employee.id,
            #             'allowance_id': alw.allowance_id.id,
            #             'type': alw.type,
            #             'expired': False,
            #             'active': True,
            #         })
            #         new_allow_rec = self.env['hr.emp.salary.allowances'].create(allow_vals)
            #         new_contract['allowance_ids'] = ([(4, new_allow_rec.id)])
            #
            # if old_contract.deduction_ids:
            #     for deduct in old_contract.deduction_ids:
            #         deduct_vals = ({
            #             'contract_id': new_contract.id,
            #             'employee_id': employee.id,
            #             'deduction_id': deduct.deduction_id.id,
            #             'type': deduct.type,
            #             'expired': False,
            #         })
            #         new_deduct_rec = self.env['hr.emp.salary.deductions'].create(deduct_vals)
            #         new_contract['deduction_ids'] = ([(4, new_deduct_rec.id)])
            if new_contract:
                # Call a Function to generate the Employee Tax Schedule
                new_contract.create_employee_tax_schedule(r_flag=True)
                new_contract.action_open()

    @api.depends('line_ids')
    def _compute_total_records(self):
        for rec in self:
            total = 0
            if rec.line_ids:
                total = len(rec.line_ids)
            rec.total_records = total

    @api.depends('line_ids', 'line_ids.grade', 'line_ids.new_grade', 'line_ids.stage', 'line_ids.new_stage')
    def _compute_grade_change_summary(self):
        for rec in self:
            total = 0
            summary_detail = ''
            if rec.line_ids:
                summary_detail = """
                            <table class="table">
                                <tbody>
                                    <tr style="text-align:left;font-size:15;background-color: #17134e;color: white;">
                                       <th>Sr#.</th>
                                       <th>Grade</th>
                                       <th>Stage</th>
                                       <th>New Grade</th>
                                       <th>New Stage</th>
                                       <th>Count</th>
                                   </tr>
                        """
                sr = 1
                results = None
                self.env.cr.execute("""select count(*) as cnt,grade,stage,new_grade, new_stage from hr_grade_change_line where grade_change_id=%s group by grade, stage, new_grade, new_stage""" % rec.id)
                results = self.env.cr.dictfetchall()

                if results is not None:
                    for result in results:
                        total += result['cnt'] and result['cnt'] or 0
                        summary_detail += """
                                    <tr style="text-left:center;font-size:15;">
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                    </tr>
                                """ % (sr, result['grade'], result['stage'], result['new_grade'], result['new_stage'], result['cnt'])
                        sr += 1
                summary_detail += """ 
                            <tr style="text-align:left;font-size:18;background-color: #17134e;color: white;">
                                <td></td>
                                <td></td>
                                <td></td>
                                <td></td>
                                <td></td>
                                <td>%s</td>
                            </tr>
                            </tbody>
                            </table> """ % total
            rec.grade_change_summary = summary_detail

    @api.model
    def default_get(self, fields):
        res = super(HRGradeChange, self).default_get(fields)
        if res.get('type') and self.env.context.get('type'):
            res['type'] = self.env.context.get('type')
        return res


class HRGradeChangeLine(models.Model):
    _name = "hr.grade.change.line"
    _description = 'Employee Grade Change Lines'

    sequence = fields.Integer('Sequence')
    grade_change_id = fields.Many2one('hr.grade.change', string='Change ID')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Job Title')
    grade = fields.Many2one('hr.payscale', string='Grade')
    grade_stages = fields.Integer('Total Stages', related='grade.stages')
    stage = fields.Integer(string='Stage')
    new_grade = fields.Many2one('hr.payscale', string='New Grade')
    new_grade_stages = fields.Integer('New Total Stages', related='new_grade.stages')
    new_stage = fields.Integer(string='New Stage')
    state = fields.Selection(related='grade_change_id.state', store=True)
    no_action = fields.Boolean('No Action', default=False)
    increment_no = fields.Integer('Increments', group_operator=False, default=1)
    personal_pay_count = fields.Integer('Personal Pays')
    basic_salary = fields.Float('Basic Pay', compute='_compute_basic_salary', store=True)
    new_basic_salary = fields.Float('New Basic Pay', compute='_compute_basic_salary', store=True)
    increment_amount = fields.Float('Increment Amount', compute='_compute_basic_salary', store=True)
    remarks = fields.Char('Remarks')

    _sql_constraints = [('name_uniq', 'UNIQUE(employee_id,grade_change_id)', 'Duplicate Records are not Allowed.')]

    @api.onchange('employee_id')
    def employee_change(self):
        if self.employee_id:
            self.grade = self.employee_id.payscale_id.id
            self.stage = self.employee_id.stage
            self.personal_pay_count = self.employee_id.personal_pay_count
            if self.grade_change_id.type=='increment':
                self.new_grade = self.employee_id.payscale_id.id

    @api.onchange('employee_id', 'grade', 'stage', 'increment_no', 'grade_change_id.promotion_type')
    def employee_change_grade(self):
        # For Incremental
        if self.grade_change_id and self.grade_change_id.type=='increment':
            new_stage = self.stage + self.increment_no
            if new_stage <= self.new_grade.stages:
                self.new_stage = new_stage
            else:
                self.new_stage = self.new_grade.stages
                self.personal_pay_count = self.employee_id.personal_pay_count + 1

        # For Promotion
        if self.grade_change_id and self.grade_change_id.type=='promotion':
            basic_salary = 0
            contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                          ('state', 'in', ('draft', 'open'))
                                                          ], order='id desc', limit=1)
            if contract_id:
                basic_salary = contract_id.wage
            if self.grade_change_id.promotion_type=='active_promotion':
                if self.grade:
                    new_grade_name = ''
                    grade_list = self.grade.name.split("-")
                    lst_grade_ele = grade_list[-1:]
                    lst_grade_ele = str(int(lst_grade_ele[0]) + 1)
                    for i in range(len(grade_list) - 1):
                        new_grade_name += grade_list[i]
                    new_grade_name = new_grade_name + "-" + lst_grade_ele
                    if new_grade_name:
                        new_grade_id = self.env['hr.payscale'].search([('name', '=', new_grade_name)])
                        if new_grade_id:
                            self.new_grade = new_grade_id.id
                            for s in range(self.new_grade.stages + 1):
                                if (new_grade_id.basic_pay + (s * new_grade_id.increment)) > basic_salary:
                                    self.new_stage = s
                                    break

            if self.grade_change_id.promotion_type=='regular_promotion':
                if self.grade:
                    new_grade_name = ''
                    grade_list = self.grade.name.split("-")
                    lst_grade_ele = grade_list[-1:]
                    lst_grade_ele = str(int(lst_grade_ele[0]) + 1)
                    for i in range(len(grade_list) - 1):
                        new_grade_name += grade_list[i]
                    new_grade_name = new_grade_name + "-" + lst_grade_ele
                    if new_grade_name:
                        new_grade_id = self.env['hr.payscale'].search([('name', '=', new_grade_name)])
                        if new_grade_id:
                            self.new_grade = new_grade_id.id
                            for s in range(self.new_grade.stages + 1):
                                if (new_grade_id.basic_pay + (s * new_grade_id.increment)) > basic_salary:
                                    self.new_stage = s + 1
                                    break

    @api.depends('employee_id', 'new_grade', 'new_stage')
    def _compute_basic_salary(self):
        for rec in self:
            if rec.employee_id:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', 'in', ('draft', 'open'))])
                if contract_id:
                    rec.basic_salary = contract_id.wage
            if rec.new_grade and rec.new_stage:
                rec.new_basic_salary = rec.new_grade.basic_pay + (rec.new_grade.increment * rec.new_stage)
            if rec.new_basic_salary > 0:
                rec.increment_amount = rec.new_basic_salary - rec.basic_salary
