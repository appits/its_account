from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_invoice_or_refund(self):
        """
        Validates if the journal entry is an invoice or a refund.
        """

        return self.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']

    @api.constrains('line_ids')
    def _check_analytic_accounts(self):
        """
        Validates if the analytic accounts of the journal entry lines are allowed in the group.
        :return: Lockout message if not allowed accounts are obtained
        """
        final_message = ''
        total_wrong_analytics_accounts = []


        if not self._check_invoice_or_refund():
            return

        i = 0
        for line in self.invoice_line_ids:
            i += 1
            if line.analytic_account_id:
                if line.account_id.analytic_account_ids:
                    if line.analytic_account_id not in line.account_id.analytic_account_ids:
                        data = {
                            'line': i,
                            'id': line.account_id.id,
                            'name': line.account_id.name,
                            'code': line.account_id.code,
                            'analytic_id': line.analytic_account_id.id,
                            'analytic': line.analytic_account_id.name,
                            'analytic_code': line.analytic_account_id.code,
                        }
                        total_wrong_analytics_accounts.append(data)
        if total_wrong_analytics_accounts:
            line_message = ''
            final_message = "No se puede crear el registro:" + "\n" + "En las líneas del asiento se están asociando cuentas analíticas que no pertenecen al grupo de cuentas permitidas a la cuenta contable asociada. " + '\n' + "Para ver esta asocianción de varias cuentas analíticas a una cuenta contable diríjase al maestro de cuentas contables en el plan de cuentas. " + '\n' + '\n' 
            for account in total_wrong_analytics_accounts:
                line_message += _('En la línea ' + f"{account['line']}" + ' se está intentando asociar las siguientes cuentas: ' + "\n"  + "\n"  + ' Cuenta contable: ' + f"{account['code']}" + ' ' + f"{account['name']}" + '    - ' + '     Cuenta analítica: ' +  f"{account['analytic_code']}" + ' ' + f"{account['analytic']}" + "\n" + "\n") 
            final_message += line_message
            
            raise UserError(_(final_message))


    @api.constrains('line_ids')
    def _check_analytic_accounts(self):
        """
        Validates if the analytic accounts of the journal entry lines are allowed in the group.
        :return: Lockout message if not allowed accounts are obtained
        """


        if not self._check_invoice_or_refund():
            return

        total_wrong_analytics_accounts = []

        i = 0

        for line in self.invoice_line_ids:
            i += 1
            if line.analytic_account_id:
                if line.account_id.analytic_account_ids:
                    if line.analytic_tags_id not in line.account_id.analytic_tag_ids:
                        data = {
                            'line': i,
                            'id': line.account_id.id,
                            'name': line.account_id.name,
                            'code': line.account_id.code,
                            'analytic_id': line.analytic_account_id.id,
                            'analytic': line.analytic_account_id.name,
                            'analytic_code': line.analytic_account_id.code,
                        }
                        total_wrong_analytics_accounts.append(data)

    def action_post(self):
        """
        Validates if the accounts of the journal entry lines are not in Blocked status, either manual or total.
        :return: Lockout message if locked accounts are obtained
        """
        final_message = ''

        total_wrong_analytics_accounts = []

        i = 0
        for line in self.line_ids:
            i += 1
            if line.analytic_account_id:
                if line.account_id.analytic_account_ids:
                    if line.analytic_account_id not in line.account_id.analytic_account_ids:
                        data = {
                            'line': i,
                            'id': line.account_id.id,
                            'name': line.account_id.name,
                            'code': line.account_id.code,
                            'analytic_id': line.analytic_account_id.id,
                            'analytic': line.analytic_account_id.name,
                            'analytic_code': line.analytic_account_id.code,
                        }
                        total_wrong_analytics_accounts.append(data)

        if total_wrong_analytics_accounts:
            line_message = ''
            final_message = "No se puede crear el registro:" + "\n" + "En las líneas del asiento se están asociando cuentas analíticas que no pertenecen al grupo de cuentas permitidas a la cuenta contable asociada. " + '\n' + "Para ver esta asocianción de varias cuentas analíticas a una cuenta contable diríjase al maestro de cuentas contables en el plan de cuentas. " + '\n' + '\n' 
            for account in total_wrong_analytics_accounts:
                line_message += _('En la línea ' + f"{account['line']}" + ' se está intentando asociar las siguientes cuentas: ' + "\n"  + "\n"  + ' Cuenta contable: ' + f"{account['code']}" + ' ' + f"{account['name']}" + '    - ' + '     Cuenta analítica: ' +  f"{account['analytic_code']}" + ' ' + f"{account['analytic']}" + "\n" + "\n") 
            final_message += line_message
            
            raise UserError(_(final_message))
        res =  super().action_post()
        return res