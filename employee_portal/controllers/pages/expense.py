import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb
import datetime
from datetime import datetime as dt, timedelta


class EmployeeExpense(http.Controller):
    @http.route(['/add/expense'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_add_expense(self, **kw):
        try:


            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            expense_product = http.request.env['product.product'].sudo().search([('can_be_expensed', '=', True)])
            values.update({
                'expense_product': expense_product,
            })
            return http.request.render('employee_portal.employee_add_expense', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

    @http.route(['/employee/expense/save'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def employee_expense_save(self, **kw):
        try:
            values, success, employee = main.prepare_portal_values(request)
            expense_data = {
                'name': kw.get('name'),
                'product_id': int(kw.get('product')),
                'reference': kw.get('bill_reference'),
                'unit_amount': kw.get('unit_price'),
                'quantity': kw.get('quantity'),
                'date': kw.get('expense_date'),
                'employee_id': employee.id,

            }
            expense_id = http.request.env['hr.expense'].sudo().create(expense_data)
            expense_id.action_submit_expenses()
            expense_id.sheet_id.action_submit_sheet()
            # expense_id.attach_document()
            # # kw.get('attach_file')
            # # pdb.set_trace()
            # attach = {
            #     'datas': kw.get('attach_file'),
            #     'res_model': 'hr.expense',
            #     'res_id': expense_id.id,
            # }
            # http.request.env['ir.attachment'].sudo().create(attach)
            data = {
                'status_is': 'Success',
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                'status_is': 'Error',
                'error_message': e.args[0] or False
            }
            data = json.dumps(data)
            return data

    @http.route(['/all/expense'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_all_expense(self, **kw):
        try:

            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)
            expenses = http.request.env['hr.expense'].sudo().search([('employee_id', '=', employee.id)])
            values.update({
                'expenses': expenses,
            })
            return http.request.render('employee_portal.employee_expenses', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web_bootstrap.portal_error', values)

    @http.route(['/get/planning/data'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def employee_planning_data(self, **kw):

        try:

            values, success, employee = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web_bootstrap.portal_error", values)

            expenses = http.request.env['account.analytic.line'].sudo().search([('employee_id', '=', employee.id),'|',('task_id.name','=','Meeting'),('task_id.name','=','Training')])
            date_from = date.today() - datetime.timedelta(days=6)
            data_list = '['
            count = 7

            while(count):
                expenses = http.request.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', employee.id), ('date','=',date_from), '|', ('task_id.name', '=', 'Meeting'),
                     ('task_id.name', '=', 'Training')])
                if expenses:
                    expense_count = 0
                    for expense in expenses:
                        expense_count += expense.unit_amount
                    if count != 1:
                        data_list += '["'+str(date_from)+'",'+str((expense_count))+'],'
                    elif count == 1:
                        data_list += '["'+str(date_from)+'",'+str((expense_count))+']]'

                else:
                    if count != 1:
                        data_list += '["'+str(date_from)+'",'+str(0)+'],'
                    elif count == 1:
                        data_list += '["'+str(date_from)+'",'+str(0)+']]'


                date_from = date_from + datetime.timedelta(days=1)
                count = int(count) - 1


            # pdb.set_trace()
            data = {
                'data_list':data_list,
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                'status_is': 'Error',
                'error_message': e.args[0] or False
            }
            data = json.dumps(data)
            return data