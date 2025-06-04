from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountAsset(models.Model):

    _inherit = 'account.asset'

    allowed_analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Cuentas Analíticas Permitidas',
        compute='_compute_allowed_analytic',
        store=False,
    )
    allowed_analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Etiquetas Analíticas Permitidas',
        compute='_compute_allowed_analytic',
        store=False,
    )

    @api.depends('account_asset_id')
    def _compute_allowed_analytic(self):

        for asset in self:

            asset_account = asset.account_asset_id

            enforce_analytic_group = asset_account.enforce_analytic_account_grouping

            if not enforce_analytic_group:
                asset.allowed_analytic_account_ids = self.env['account.analytic.account'].search([]).ids
                asset.allowed_analytic_tag_ids = self.env['account.analytic.tag'].search([]).ids
            else:
                if asset_account:
                    asset.allowed_analytic_account_ids = asset_account.analytic_account_ids.ids
                    asset.allowed_analytic_tag_ids = asset_account.analytic_tag_ids.ids
                else:
                    asset.allowed_analytic_account_ids = False
                    asset.allowed_analytic_tag_ids = False

    @api.constrains('account_analytic_id', 'analytic_tag_ids')
    def _enforce_configured_analytic_rules(self):

        for asset in self:

            account = asset.account_analytic_id

            if account.enforce_analytic_account_or_tag and (asset.account_analytic_id and asset.analytic_tag_ids):
                raise ValidationError(
                    "Solo puedes seleccionar una cuenta analítica o una etiqueta analítica, no ambas a la vez.")

            if account.block_empty_analytic_account_or_tag and not (asset.account_analytic_id or asset.analytic_tag_ids):
                raise ValidationError("Debes seleccionar una cuenta analítica o una etiqueta analítica.")
        