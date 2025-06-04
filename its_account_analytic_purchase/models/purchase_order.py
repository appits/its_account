from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'


    def button_confirm(self):

        for purchase in self:
            purchase._check_move_analytic_constraints()

        return super(self).button_confirm()


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

