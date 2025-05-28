from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'

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

        # total_wrong_analytics_accounts = []
        # i = 0
        # for line in self.invoice_line_ids:
        #     i += 1
        #     if line.analytic_account_id:
        #         if line.account_id.account_analytic_ids:
        #             if line.analytic_account_id not in line.account_id.account_analytic_ids:
        #                 data = {
        #                     'line': i,
        #                     'id': line.account_id.id,
        #                     'name': line.account_id.name,
        #                     'code': line.account_id.code,
        #                     'analytic_id': line.analytic_account_id.id,
        #                     'analytic': line.analytic_account_id.name,
        #                     'analytic_code': line.analytic_account_id.code,
        #                 }
        #                 total_wrong_analytics_accounts.append(data)
        # if total_wrong_analytics_accounts:
        #     line_message = ''
        #     final_message = "No se puede crear el registro:" + "\n" + "En las líneas del asiento se están asociando cuentas analíticas que no pertenecen al grupo de cuentas permitidas a la cuenta contable asociada. " + '\n' + "Para ver esta asocianción de varias cuentas analíticas a una cuenta contable diríjase al maestro de cuentas contables en el plan de cuentas. " + '\n' + '\n' 
        #     for account in total_wrong_analytics_accounts:
        #         line_message += _('En la línea ' + f"{account['line']}" + ' se está intentando asociar las siguientes cuentas: ' + "\n"  + "\n"  + ' Cuenta contable: ' + f"{account['code']}" + ' ' + f"{account['name']}" + '    - ' + '     Cuenta analítica: ' +  f"{account['analytic_code']}" + ' ' + f"{account['analytic']}" + "\n" + "\n") 
        #     final_message += line_message
            
        #     raise UserError(_(final_message))
        