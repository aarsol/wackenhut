import pdb
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class RecomputeEmployeeContractWiz(models.TransientModel):
    _name = 'recompute.employee.contract.wiz'
    _description = 'Employee Contract Recompute Wizard'

    def _get_contract_ids(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    contract_ids = fields.Many2many('hr.contract', 'recompute_employee_contract_rel1', 'wizard_id', 'contract_id', 'Contracts', default=_get_contract_ids)

    def action_recompute_employee_contracts(self):
        for rec in self:
            if rec.contract_ids:
                for contract_id in rec.contract_ids:
                    if contract_id.state not in ('done', 'cancel'):
                        _logger.info('.......Contract for the Employee %r-%r is recomputed . ..............', contract_id.employee_id.name, contract_id.employee_id.name)
                        contract_id.recompute_allowances_deductions()
