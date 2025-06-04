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

    enforce_analytic_account_grouping = fields.Boolean(
        "Forzar agrupamiento de cuentas analiticas en los registros",
        default=False,
        help="Si esta opción está activada, se forzará el uso de la cuenta analitica en los registros"
    )

    enforce_analytic_account_or_tag = fields.Boolean(
        "Forzar que no se pueda seleccionar cuenta analitica y etiqueta analitica a la vez",
        default=False,
        help="Si esta opción está activada, se forzará el uso de la cuenta analitica o etiqueta analitica en los registros"
    )

    block_empty_analytic_account_or_tag = fields.Boolean(
        "Bloquear cuenta analitica o etiqueta analitica vacia en los registros",
        default=False,
        help="Si esta opción está activada, se solicitará una cuenta analitica o etiqueta analitica en los registros"
    )
