from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    state = fields.Selection(
        [
            ("free", "Free"),
            ("total_block", "Total block"),
            ("manual_block", "Manual block"),
        ],
        string="State",
        default="free",
    )