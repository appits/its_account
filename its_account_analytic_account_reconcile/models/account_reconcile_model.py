from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):

    _inherit = 'account.reconcile.model.line'

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

    @api.depends('account_id')
    def _compute_allowed_analytic(self):

        for line in self:

            line_account = line.account_id

            enforce_analytic_group = self.env['ir.config_parameter'].sudo().get_param(
                'its_account_analytic.enforce_analytic_account_grouping'
            )

            if not enforce_analytic_group:
                line.allowed_analytic_account_ids = self.env['account.analytic.account'].search([]).ids
                line.allowed_analytic_tag_ids = self.env['account.analytic.tag'].search([]).ids
            else:
                if line_account:
                    line.allowed_analytic_account_ids = line_account.analytic_account_ids.ids
                    line.allowed_analytic_tag_ids = line_account.analytic_tag_ids.ids
                else:
                    line.allowed_analytic_account_ids = False
                    line.allowed_analytic_tag_ids = False

    @api.constrains('analytic_account_id', 'analytic_tag_ids')
    def _enforce_configured_analytic_rules(self):

        for line in self:


            account = line.account_id

            if account.enforce_analytic_account_or_tag and (line.analytic_account_id and line.analytic_tag_ids):
                raise ValidationError(
                    "Solo puedes seleccionar una cuenta analítica o una etiqueta analítica, no ambas a la vez.")

            if account.block_empty_analytic_account_or_tag and not (line.analytic_account_id or line.analytic_tag_ids):
                raise ValidationError("Debes seleccionar una cuenta analítica o una etiqueta analítica.")