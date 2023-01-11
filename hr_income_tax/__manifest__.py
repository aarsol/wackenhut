{
    'name': 'HR EMPLOYEE INCOME TAX',
    'version': '14.0.1',
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

        'views/hr_income.xml',
        'views/hr_employee_income_tax_view.xml',
        'views/hr_employee_income_tax_adjustment_view.xml',
        'views/hr_employee_annual_income_adjustment_view.xml',
        'views/tax_cpr_no_view.xml',
        'views/res_config_setting_view.xml',
        'views/hr_contract_view.xml',

        'wizards/generate_employee_income_tax_wiz_view.xml',

        'reports/employee_income_tax_statement_report.xml',
        'reports/report.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
