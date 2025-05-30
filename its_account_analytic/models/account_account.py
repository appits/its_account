from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    # analytic accounts
    analytic_account_ids = fields.Many2many('account.analytic.account', 'analytic_account_ids_rel', 'account_id',
                                            'analytic_id', store=True, string='Analytic accounts', help='Analytic accounts')
    # analytic tags

    analytic_tag_ids = fields.Many2many('account.analytic.tag', 'account_analytic_tag_ids_rel', 'account_id',
                                         'analytic_tag_id', store=True, string='Analytic tags', help='Analytic tags')
