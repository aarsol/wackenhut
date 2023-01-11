# -*- coding: utf-8 -*-
{
    'name': "Employee Request",
    'summary': """
        Employee Request""",

    'description': """
        Employee Request
    """,

    'author': "AARSOL",
    'website': "http://www.aarsol.com",
    'category': 'HR',
    'version': '0.1',

    'depends': [
        'base',
        'mail',
        'resource',
        'hr',
        'hr_holidays',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/base_groups.xml',
        # 'security/special_request.xml',

        # 'data/data.xml',
        # 'data/sequence.xml',
        # 'data/time_off_data.xml',
        # 'data/employee_request_activity.xml',

        # 'views/views.xml',
        # 'views/missed_attendance_view.xml',
        # 'views/medical_advance.xml',
        #
        # 'views/noc_request.xml',
        # 'views/travel_request.xml',
        # 'views/templates.xml',
        # 'views/inht_leave_allocation.xml',
        # 'views/marriage_grant.xml',
        # 'views/resign_request.xml',
        # 'views/ucp_leave_request.xml',
        # 'views/loan_advance.xml',
        #
        # 'reports/employee_leave_detail_report.xml',
        # 'reports/employee_leave_report.xml',
        # 'reports/noc_report.xml',
        # 'reports/marriage_report.xml',
        # 'reports/report_view.xml',
        # 'reports/missed_attendance_report.xml',
        #
        # 'wizards/missed_attendance_rep_wiz.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': 'true',
    'sequence': '10',
}
