# -*- coding: utf-8 -*-
{
    'name': "Employee Notifications",

    'version': '13.0.1.0.1',
    'summary': """Employee Notification Module""",
    'description': 'Employee Notifications',
    'category': 'OdooCMS',
    'sequence': 34,
    'author': "Umair Khalid Software Developer",
    'company': 'AARSOL',
    'website': "https://aarsol.com/",

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/employee_notification_security.xml',
        'views/views.xml',
        'views/menu_employee_notifications.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
