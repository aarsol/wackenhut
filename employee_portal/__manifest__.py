# -*- coding: utf-8 -*-
{
    'name': "Employee Portal",
    'summary': """
        Faculty Web Portal""",
    'description': """
        Faculty Web Portal
    """,
    'author': "Umair Khalid,Umair Mukhtar",
    'company': 'AARSOL & NUST (Joint Venture)',
    'website': "https://www.aarsol.com",
    'category': 'OdooCMS',
    'version': '1.0',
    'sequence': '1',
    'application': 'true',
    'depends': ['website', 'employee_notification', 'hr_holidays',
                'odoocms_web_bootstrap', 'hr_attendance'],  # 'aarsol_hr_performace'
    'data': [
        'views/assets.xml',
        'views/dashboard/employee_dashboard.xml',
        'views/component/components.xml',
        'views/layout/layout_page.xml',
        'views/sidebar/sidebar.xml',
        'views/pages/attendance.xml',
        'views/component/topbar.xml',
        'views/pages/profile.xml',
        'views/pages/leave.xml',
        'views/pages/leave_request.xml',
        'views/pages/timesheet_status.xml',
        'views/pages/timesheet_creation.xml',
        'views/pages/planning.xml',
        'views/pages/add_expenses.xml',
        'views/pages/all_expenses.xml',
        'views/pages/notifications.xml',
    ],
}
