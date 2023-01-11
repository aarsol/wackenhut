{
    'name': 'HR Payroll GL Setting',
    'version': '14.0.1',
    'category': 'Human Resources/Payroll',
    'sequence': 5,
    'summary': 'Generic Payroll system Integrated with Accounting.',
    'author': 'AARSOL',
    'website': 'https://aarsol.com/',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base', 'mail', 'hr_payroll', 'account_accountant'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'menus/menu.xml',

        'views/hr_employee_account_heads_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_payroll_rule_heads_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
