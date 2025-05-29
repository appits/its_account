from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):

        products = []
        for rec in vals['move_ids_without_package']:
            # Búsquedad del producto para evaluar el estado de la cuenta contable asociada a este está bloqueado
            prod_prod = rec[2]['product_id']
            self._cr.execute('SELECT product_tmpl_id FROM public.product_product WHERE id = %s', [prod_prod])
            product_template = int(''.join(map(str, self._cr.fetchone())))
            products.append(product_template)

            # Búsquedad de la cuenta analítica para evaluar si tiene estado bloqueado
            prod_prod = rec[2]['product_id']
            self._cr.execute('SELECT state FROM public.account_analytic_account WHERE id = %s', [prod_prod])
        products = tuple(products)
        company = str(self.env.company.id)
        picking_type = str(vals['picking_type_id'])
        self.env.cr.execute('SELECT code FROM public.stock_picking_type WHERE id = %s', (picking_type,))
        code_type = self.env.cr.dictfetchall()[0]['code']

        query = """

                with irpp as
                         (select cast(substring(irp.res_id from '[0-9].*') as int)          as pc_id, \
                                 cast(substring(irp.value_reference from '[0-9].*') as int) as account_id \
                          from ir_property as irp \
                          where irp.company_id = %s AND \
                                (%s = 'incoming' AND irp.name IN ('property_stock_account_input_categ_id', \
                                                                  'property_stock_valuation_account_id')) \
                             OR (%s = 'outgoing' AND irp.name IN ('property_stock_account_output_categ_id', \
                                                                  'property_stock_valuation_account_id')) \
                             OR (%s = 'internal' AND irp.name IN ('property_stock_valuation_account_id')) \
                             OR (%s = 'mrp_operation' AND irp.name IN ('property_stock_account_output_categ_id')))

                SELECT pt.name AS product, account.name AS account, account.state AS account_state \
                FROM public.product_template AS pt \
                         LEFT JOIN product_category AS categ ON pt.categ_id = categ.id \
                         LEFT JOIN irpp AS ip ON categ.id = ip.pc_id \
                         LEFT JOIN account_account AS account ON ip.account_id = account.id
                WHERE pt.id in %s \
                  and account.state = 'total_block' """

        self.env.cr.execute(query, (company, code_type, code_type, code_type, code_type, products,))

        blocked_accounts = self.env.cr.dictfetchall()
        line_message = ''
        if blocked_accounts:
            for account in blocked_accounts:
                line_message += _(
                    ' Cuenta: ' + f"{account['account']}" + "\n" + ' Producto: ' + f"{account['product']}" + "\n" + "\n")

            raise UserError(
                _("No se puede crear el pedido porque algunas cuentas están totalmente bloqueadas: " + "\n" + "\n" + line_message))
        res = super().create(vals)
        return res