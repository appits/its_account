from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order.line'

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

    @api.depends('product_id')
    def _compute_allowed_analytic(self):
        for line in self:

            expense_acct = line.product_id.property_account_expense_id

            enforce_analytic_group = self.env['ir.config_parameter'].sudo().get_param(
                'its_account_analytic.enforce_analytic_account_grouping'
            )

            if not enforce_analytic_group:
                line .allowed_analytic_account_ids = self.env['account.analytic.account'].search([]).ids
                line.allowed_analytic_tag_ids     = self.env['account.analytic.tag'].search([]).ids
            else:
                if expense_acct:
                    line.allowed_analytic_account_ids = expense_acct.analytic_account_ids.ids
                    line.allowed_analytic_tag_ids     = expense_acct.analytic_tag_ids.ids
                else:
                    line.allowed_analytic_account_ids = False
                    line.allowed_analytic_tag_ids     = False


    @api.constrains('account_analytic_id', 'analytic_tag_ids')
    def _enforce_configured_analytic_rules(self):

        enforce_analytic_account_or_tag = self.env['ir.config_parameter'].sudo().get_param(
            'its_account_analytic.enforce_analytic_account_or_tag'
        )

        block_empty_analytic_account_or_tag = self.env['ir.config_parameter'].sudo().get_param(
            'its_account_analytic.block_empty_analytic_account_or_tag'
        )

        for line in self:

            if enforce_analytic_account_or_tag and (line.account_analytic_id and line.analytic_tag_ids):
                raise ValidationError("Solo puedes seleccionar una cuenta analítica o una etiqueta analítica, no ambas a la vez.")

            if block_empty_analytic_account_or_tag and not (line.account_analytic_id or line.analytic_tag_ids):
                raise ValidationError("Debes seleccionar una cuenta analítica o una etiqueta analítica.")

    def button_confirm(self):

        res = super().button_confirm()

        return res