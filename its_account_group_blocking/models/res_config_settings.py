
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    force_analytic_account = fields.Boolean(
        "Forzar cuenta analitica en los registros",
        default=False,
        help="Si esta opción está activada, se forzará el uso de la cuenta analitica en los registros",
        config_parameter="its_account_group_blocking.force_analytic_account"
    )