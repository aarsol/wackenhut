{
    'name': 'AARSOL HR Extentsion',
    'version': '14.0.1.0.1',
    'summary': """Customized Feature of Human Resource Module""",
    'description': 'AARSOL HR Extentsion Module',
    'category': 'hr',
    'sequence': 2,
    'author': 'AARSOL',
    'company': 'AARSOL',
    'website': "http://www.aarsol.com/",
    'depends': ['hr', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'menus/hr_ext_menu.xml',

        'views/hr_allowance_deduction_view.xml',
        'views/hr_payscale_view.xml',
        'views/hr_section_category_view.xml',

        'views/hr_view.xml',
        'views/hr_salary_inputs_view.xml',
        'views/hr_payslip_view.xml',

        'views/res_config_setting_view.xml',
        'views/hr_gp_fund_view.xml',
        'views/hr_bank_view.xml',
        'views/hr_payslip_cron_view.xml',
        'views/hr_salary_allowances_template_view.xml',
        'views/hr_salary_deductions_template_view.xml',
        'views/hr_employee_payroll_status_view.xml',
        'views/hr_employee_multi_menus_view.xml',
        'views/hr_promotion_view.xml',
        'views/hr_employee_backdate_arrears_view.xml',
        'views/hr_employee_half_pay_view.xml',
        'views/hr_payslip_batch_view.xml',
        'views/hr_payslip_advice_view.xml',
        'views/hr_employee_disability_view.xml',
        'views/hr_employee_religion_view.xml',

        'reports/report.xml',
        'reports/gp_fund_statement_report.xml',
        'reports/allowance_report.xml',
        'reports/deduction_report.xml',
        'reports/topsheet_allowance_report.xml',
        'reports/topsheet_deduction_report.xml',
        # 'reports/product_barcode.xml',
        'reports/grade_change_report.xml',

        'wizard/wps_view.xml',
        'wizard/hr_inputs_wizard_view.xml',
        'wizard/gp_fund_wiz.xml',
        'wizard/gp_fund_statement_wiz.xml',
        'wizard/allowance_wiz.xml',
        'wizard/deduction_wiz.xml',
        'wizard/top_sheet_allowance_wiz.xml',
        'wizard/top_sheet_deduction_wiz.xml',
        'wizard/ministerial_staff_deduction.xml',
        'wizard/promote_wiz.xml',
        'wizard/employee_data_rep_view.xml',
        'wizard/promote_bulk_wiz.xml',
        'wizard/payslips_cron_wizard_view.xml',

        'wizard/hr_data_import_view.xml',

        'wizard_new/employee_status_change_wiz.xml',
        'wizard_new/employee_backdate_arrears_confirm_wiz.xml',
        'wizard_new/bulk_employee_backdate_arrears_wiz.xml',
        'wizard_new/generate_payslip_wiz_view.xml',
        'wizard_new/hr_emp_salary_inputs_import_wizard_view.xml',
        'wizard_new/hr_emp_salary_inputs_installments_wizard_view.xml',
        'wizard_new/hr_emp_salary_allowances_addition_wizard_view.xml',
        'wizard_new/hr_emp_salary_deductions_addition_wizard_view.xml',
        'wizard_new/hr_emp_salary_allowances_expiry_wizard_view.xml',
        'wizard_new/recompute_employee_contract_wiz_view.xml',

        'data/data.xml',
        'data/email_templates.xml',
        'data/sequence.xml',

    ],
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
