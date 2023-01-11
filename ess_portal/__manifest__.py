# -*- coding: utf-8 -*-
{
    'name': "ESS Portal",
    'summary': """
        Employee Web Portal""",
    'description': """
        Employee Self Service Web Portal
    """,
    'author': "Sulman Shaukat &amp; Farooq Arif",
    'company': 'AARSOL & NUST (Joint Venture)',
    'website': "https://www.aarsol.com",
    'category': 'OdooCMS',
    'version': '15.0.0.1',
    'sequence': '1',
    'application': 'true',
    'depends': ['website','ess_portal_assets','cms_notifications'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/portal_security.xml',
        'views/component/header_menu.xml',
        'views/component/right_menu.xml',
        'views/component/side_menu.xml',
        'views/component/quick_actions.xml',
        'views/component/layout.xml',
        'views/component/portal_error.xml',
        'views/profile/profile.xml',
        'views/dashboard/dashboard.xml',
        'views/profile/family.xml',
        'views/leave/leave.xml',
        'views/attendance/attendance.xml',
        'views/request/request.xml',
        'views/payment/payment.xml',
        'views/request/team_requests.xml',
        'views/team/team_organo.xml',
        'views/reports/reports.xml',
        'views/portal_view.xml',
        'views/notification/notification.xml',
    ],
}
