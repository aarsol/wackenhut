{
    'name': 'Leaves Extension',
    'version': '14.0.1',
    'sequence': 3,
    'category': 'Human Resources/Employees',
    'author': 'AARSOL',
    'website': 'https://aarsol.com/',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base', 'mail', 'hr', 'hr_holidays'
    ],
    'data': [
          'views/hr_leaves.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
