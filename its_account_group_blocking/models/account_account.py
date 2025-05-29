from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_analytic_ids = fields.Many2many('account.analytic.account', 'account_analytic_ids_rel', 'account_id',
                                            'analytic_id', store=True, string='Analytic accounts', help='Analytic accounts')
    has_analytic_accounts =  fields.Boolean(string='Has analytic accounts?', default=False, help='Tells if the account has analytic accounts associated')

    @api.onchange('has_analytic_accounts')
    def _onchange_has_analytic_accounts(self):
        if not self.has_analytic_accounts:
            self.account_analytic_ids = False