from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):

    _inherit = 'account.move'


    def action_post(self):

        for move in self:
            move._check_move_analytic_constraints()

        return super(AccountMove, self).action_post()



    def _check_move_analytic_constraints(self):

        self.ensure_one()

        lines = None

        if self.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']:
            lines = self.invoice_line_ids
        else:
            lines = self.line_ids

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