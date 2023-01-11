{
    'name': 'HR EMPLOYEE PROMOTION',
    'version': '14.0.1.0.1',
    'summary': """Customized Feature of Human Resource Module""",
    'description': 'HR Employee Promotion & Transfer Module',
    'category': 'hr',
    'sequence': 10,
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'depends': ['hr', 'aarsol_hr_ext'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',

        'views/hr_employee_promotion_type_view.xml',
        'views/hr_employee_promotion_view.xml',
        'views/hr_employee_demotion_view.xml',

        'views/hr_employee_transfer_type_view.xml',
        'views/hr_employee_transfer_view.xml',

        'views/hr_employee_view.xml',


        'wizards/employee_promotion_wizard_view.xml',
        'wizards/employee_demotion_wizard_view.xml',
        'wizards/employee_transfer_wizard_view.xml',

        'reports/employee_promotion_report.xml',
        'reports/employee_demotion_report.xml',
        'reports/report_view.xml',

    ],
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
