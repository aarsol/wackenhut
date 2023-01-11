{
    'name': 'HR GRATUITY',
    'version': '14.0.1',
    'sequence': 3,
    'category': 'Human Resources/Employees',
    'author': 'AARSOL',
    'website': 'https://aarsol.com/',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base', 'mail', 'hr','hr_payroll'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'menu/menu.xml',

        'views/hr_gratuity_config_type_view.xml',
        'views/hr_gratuity_config_view.xml',
        'views/res_config_setting_view.xml',

        'wizard/gratuity_report_wiz_view.xml',

        'reports/gratuity_report.xml',
        'reports/report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
