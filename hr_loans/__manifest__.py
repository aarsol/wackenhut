{
    'name': 'HR LOANS AND ADVANCES',
    'version': '14.0.1',
    'category': 'Invoicing',
    'sequence': 3,
    'category': 'Human Resources/Employees',
    'author': 'AARSOL',
    'website': 'https://aarsol.com/',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base', 'mail', 'hr', 'hr_payroll'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'menu/menu.xml',

        # Used in hr_loan view
        'wizard/calc_guarantor_gratuity_wiz_view.xml',

        'views/hr_staff_advance_view.xml',
        'views/hr_loan_view.xml',
        'views/hr_loan_rule_view.xml',
        'views/hr_supplementary_loan_view.xml',

        'wizard/hr_loan_pause_wiz_view.xml',
        'wizard/hr_loan_reschedule_wiz_view.xml',
        'wizard/hr_loan_interest_reschedule_wiz_view.xml',
        'wizard/bulk_hr_loan_interest_reschedule_wiz_view.xml',
        'wizard/hr_loan_waiveoff_wiz_view.xml',
        'wizard/hr_loan_paid_wiz_view.xml',
        'wizard/hr_supplementary_loan_wiz_view.xml',

        'reports/employee_advance_report.xml',
        'reports/employee_loan_report.xml',
        'reports/employee_loan_paid_report.xml',
        'reports/employee_loan_unpaid_report.xml',
        'reports/report.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
