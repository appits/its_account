from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    state = fields.Selection(
        [
            ("free", "Free"),
            ("total_block", "Total block"),
            ("manual_block", "Manual block"),
        ],
        string="State",
        default="free",
    )