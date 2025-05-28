from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    account_id = fields.Many2one('account.account', string='Account', help='Account associated')