
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    enforce_analytic_account_grouping = fields.Boolean(
        "Forzar cuenta analitica en los registros",
        default=False,
        help="Si esta opción está activada, se forzará el uso de la cuenta analitica en los registros",
        config_parameter="its_account_analytic.enforce_analytic_account_grouping"
    )

    enforce_analytic_account_or_tag = fields.Boolean(
        "Forzar que no se pueda seleccionar cuenta analitica y etiqueta analitica a la vez",
        default=False,
        help="Si esta opción está activada, se forzará el uso de la cuenta analitica o etiqueta analitica en los registros",
        config_parameter="its_account_analytic.enforce_analytic_account_or_tag"
    )

    block_empty_analytic_account_or_tag = fields.Boolean(
        "Bloquear cuenta analitica o etiqueta analitica vacia en los registros",
        default=False,
        help="Si esta opción está activada, se solicitará una cuenta analitica o etiqueta analitica en los registros",
        config_parameter="its_account_analytic.block_empty_analytic_account_or_tag"
    )