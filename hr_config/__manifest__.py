{
    'name': 'OPF General Configuration',
    'version': '14.0.1',
    'category': 'Human Resources/Employees',
    'sequence': 3,
    'summary': 'Additional Features To the OPF',
    'author': 'AARSOL',
    'website': 'https://aarsol.com/',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base', 'mail', 'hr', 'hr_contract', 'hr_payroll',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/hr_location_view.xml',
        'views/hr_location_type_view.xml',
        'views/hr_province_view.xml',
        'views/hr_department_view.xml',
        'views/hr_employee_unions_view.xml',
        'views/hr_view.xml',
        'views/hr_transport_area_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
