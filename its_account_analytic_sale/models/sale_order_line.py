from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):

    _inherit = 'sale.order.line'

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

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Cuenta Analítica',
        related='order_id.analytic_account_id',
    )

    @api.depends('product_id')
    def _compute_allowed_analytic(self):

        for line in self:

            account_id = line.get_line_account()

            enforce_analytic_group = account_id.enforce_analytic_account_grouping

            if not enforce_analytic_group:
                line.allowed_analytic_account_ids = self.env['account.analytic.account'].search([]).ids
                line.allowed_analytic_tag_ids = self.env['account.analytic.tag'].search([]).ids
            else:
                if account_id:
                    line.allowed_analytic_account_ids = account_id.analytic_account_ids.ids
                    line.allowed_analytic_tag_ids = account_id.analytic_tag_ids.ids
                else:
                    line.allowed_analytic_account_ids = False
                    line.allowed_analytic_tag_ids = False

    @api.constrains('account_analytic_id', 'analytic_tag_ids')
    def _enforce_configured_analytic_rules(self):

        for line in self:

            account = line.get_line_account()

            if account.enforce_analytic_account_or_tag and (line.analytic_account_id and line.analytic_tag_ids):
                raise ValidationError(
                    "Solo puedes seleccionar una cuenta analítica o una etiqueta analítica, no ambas a la vez.")

            if account.block_empty_analytic_account_or_tag and not (line.analytic_account_id or line.analytic_tag_ids):
                raise ValidationError("Debes seleccionar una cuenta analítica o una etiqueta analítica.")

    def get_line_account(self):

        """ Returns the account to be used for this line, based on the product's category or directly from the product. """

        product = self.product_id

        account_id = None

        if product.categ_id:
            account_id = product.categ_id.property_account_income_categ_id
        else:
            account_id = product.property_account_income_id

        return account_id