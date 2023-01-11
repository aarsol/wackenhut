# -*- coding: utf-8 -*-
# from odoo import http


# class AarsolEmployeeRequest(http.Controller):
#     @http.route('/aarsol_employee_request/aarsol_employee_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aarsol_employee_request/aarsol_employee_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aarsol_employee_request.listing', {
#             'root': '/aarsol_employee_request/aarsol_employee_request',
#             'objects': http.request.env['aarsol_employee_request.aarsol_employee_request'].search([]),
#         })

#     @http.route('/aarsol_employee_request/aarsol_employee_request/objects/<model("aarsol_employee_request.aarsol_employee_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aarsol_employee_request.object', {
#             'object': obj
#         })
