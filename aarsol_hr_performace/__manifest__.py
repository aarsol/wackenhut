{
    'name': 'AARSOL HR Performance',
    'version': '14.0.1.0.1',
    'summary': """Customized Performance of Human Resource Module""",
    'description': 'AARSOL HR Performance Module',
    'category': 'hr',
    'sequence': 2,
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'depends': ['hr','aarsol_hr_ext'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_appraisal_views.xml',
        'views/hr_assessment_views.xml',
        'views/hr_employee_view.xml'
    ],
    'demo': [
        # 'demo/employee.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
