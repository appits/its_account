from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    # TODO arreglar
    @api.constrains('account_depreciation_id', 'account_depreciation_expense_id', 'account_asset_id', )
    def _check_analytic_account(self):
        for rec in self:
            if rec.account_analytic_id.state == 'total_block':
                raise UserError(_("No se puede crear el activo fijo porque algunas cuentaestán totalmente bloqueadas: " + "\n" + "\n"))
            blocked_accounts = []
            if rec.account_asset_id.state == 'total_block':
                blocked_accounts.append(rec.account_asset_id)
            if rec.account_depreciation_id.state == 'total_block':
                blocked_accounts.append(rec.account_depreciation_id)
            if rec.account_depreciation_expense_id.state == 'total_block':
                blocked_accounts.append(rec.account_depreciation_expense_id)

            if blocked_accounts:
                final_message = 'No se puede crear el modelo de activo porque algunas cuentas están totalmente bloqueadas: \n'
                for account in blocked_accounts:
                    final_message += _("\t" + f"{account.name}" + "\n") 
                raise UserError(_(final_message ))

                final_message = ''
        