from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    allowed_analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Cuentas Analíticas Permitidas',
        compute='_compute_allowed_analytic',
        store=False,
    )


    @api.depends('order_line.product_id')
    def _compute_allowed_analytic(self):
        for order in self:
            order.allowed_analytic_account_ids = order.order_line.mapped('allowed_analytic_account_ids')

    def action_confirm(self):
        for sale in self:
            sale._check_move_analytic_constraints()

        return super(SaleOrder, self).action_confirm()


    def _check_move_analytic_constraints(self):

        self.ensure_one()

        lines = self.order_line

        lines._enforce_configured_analytic_rules()

        lines._compute_allowed_analytic()

        for line in lines:

            if line.analytic_account_id and line.analytic_account_id  not in line.allowed_analytic_account_ids:
                raise ValidationError(
                    _("La cuenta analítica '%s' no está permitida para este movimiento.") % line.analytic_account_id.name
                )


            if line.analytic_tag_ids and line.analytic_tag_ids not in line.analytic_tag_ids & line.allowed_analytic_tag_ids:
                raise ValidationError(
                    _("Las etiquetas analíticas '%s' no están permitidas para este movimiento.") % ', '.join(line.analytic_tag_ids.mapped('name'))
                )