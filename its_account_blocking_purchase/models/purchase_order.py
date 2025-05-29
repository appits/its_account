from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('order_line')
    def _check_product_accounts(self):
        products = []
        analytic_accounts = []
        for line in self.order_line:
            products.append(line.product_id.product_tmpl_id.id)
            if line.account_analytic_id.state == 'total_block':
                account_already_added = False
                for line in analytic_accounts:
                    for i, name in analytic_accounts.items():
                        account_already_added = i == line.account_analytic_id.id
                if not account_already_added:
                    account = {
                        'id': line.account_analytic_id.id,
                        'name': line.account_analytic_id.name,
                    }
                    analytic_accounts.append(account)
        products = tuple(products)
        company = str(self.env.company.id)

        category_account_query = """

                                 with irpp as
                                          (select cast(substring(irp.res_id from '[0-9].*') as int)          as pc_id, \
                                                  cast(substring(irp.value_reference from '[0-9].*') as int) as account_id \
                                           from ir_property as irp \
                                           where irp.company_id = %s \
                                             AND irp.name = 'property_stock_valuation_account_id')

                                 SELECT pt.name       AS product, \
                                        account.name  AS account, \
                                        account.state AS account_state, \
                                        account.code  AS code \
                                 FROM public.product_template AS pt \
                                          LEFT JOIN product_category AS categ ON pt.categ_id = categ.id \
                                          LEFT JOIN irpp AS ip ON categ.id = ip.pc_id \
                                          LEFT JOIN account_account AS account ON ip.account_id = account.id
                                 WHERE pt.id in %s \
                                   and account.state = 'total_block'"""

        self.env.cr.execute(category_account_query, (company, products,))
        blocked_category_accounts = self.env.cr.dictfetchall()

        product_account_query = """
                                with irpp as
                                         (select cast(substring(irp.res_id from '[0-9].*') as int)          as pt_id, \
                                                 cast(substring(irp.value_reference from '[0-9].*') as int) as account_id \
                                          from ir_property as irp \
                                          where irp.company_id = %s \
                                            AND (irp.name IN \
                                                 ('property_account_income_id', 'property_account_expense_id', \
                                                  'property_account_creditor_price_difference')))
                                SELECT pt.name       AS product, \
                                       account.name  AS account, \
                                       account.state AS account_state, \
                                       account.code  AS code \
                                FROM public.product_template AS pt \
                                         LEFT JOIN irpp AS ip ON pt.id = ip.pt_id \
                                         LEFT JOIN account_account AS account ON ip.account_id = account.id
                                WHERE pt.id in %s \
                                  and account.state = 'total_block'"""

        self.env.cr.execute(product_account_query, (company, products,))
        blocked_product_accounts = self.env.cr.dictfetchall()

        all_blocked_category = blocked_category_accounts + blocked_product_accounts

        line_message = ''
        if all_blocked_category or analytic_accounts:
            for account in all_blocked_category:
                line_message += _(
                    ' Cuenta: ' + f"{account['code']}" + ' ' + f"{account['account']}" + "\n" + ' Producto: ' + f"{account['product']}" + "\n" + "\n")
            for analytic in analytic_accounts:
                line_message += _(' Cuenta analítica: ' + f"{analytic['name']}" + "\n" + "\n")

            raise UserError(
                _("No se puede crear el pedido porque algunas cuentas están totalmente bloqueadas: " + "\n" + "\n" + line_message))

    def button_confirm(self):
        if self.order_line:
            products = []
            analytic_accounts = []
            for line in self.order_line:
                products.append(line.product_id.product_tmpl_id.id)
                if line.account_analytic_id.state == 'total_block':
                    account_already_added = False
                    for line in analytic_accounts:
                        for i, name in analytic_accounts.items():
                            account_already_added = i == line.account_analytic_id.id
                    if not account_already_added:
                        account = {
                            'id': line.account_analytic_id.id,
                            'name': line.account_analytic_id.name,
                        }
                        analytic_accounts.append(account)
            products = tuple(products)

            company = str(self.env.company.id)

            category_account_query = """

                                     with irpp as
                                              (select cast(substring(irp.res_id from '[0-9].*') as int)          as pc_id, \
                                                      cast(substring(irp.value_reference from '[0-9].*') as int) as account_id \
                                               from ir_property as irp \
                                               where irp.company_id = %s AND \
                                                     (%s = 'incoming' AND irp.name IN \
                                                                          ('property_stock_account_input_categ_id', \
                                                                           'property_stock_valuation_account_id')) \
                                                  OR (%s = 'internal' AND irp.name IN ('property_stock_valuation_account_id')) \
                                                  OR (%s = 'mrp_operation' AND \
                                                      irp.name IN ('property_stock_account_output_categ_id')))

                                     SELECT pt.name       AS product, \
                                            account.name  AS account, \
                                            account.state AS account_state, \
                                            account.code  AS code \
                                     FROM public.product_template AS pt \
                                              LEFT JOIN product_category AS categ ON pt.categ_id = categ.id \
                                              LEFT JOIN irpp AS ip ON categ.id = ip.pc_id \
                                              LEFT JOIN account_account AS account ON ip.account_id = account.id
                                     WHERE pt.id in %s \
                                       and account.state = 'total_block'"""

            self.env.cr.execute(category_account_query, (company, self.picking_type_id.code, self.picking_type_id.code,
                                                         self.picking_type_id.code, products,))
            blocked_category_accounts = self.env.cr.dictfetchall()

            product_account_query = """
                                    with irpp as
                                             (select cast(substring(irp.res_id from '[0-9].*') as int)          as pt_id, \
                                                     cast(substring(irp.value_reference from '[0-9].*') as int) as account_id \
                                              from ir_property as irp \
                                              where irp.company_id = %s \
                                                AND (irp.name IN \
                                                     ('property_account_income_id', 'property_account_expense_id', \
                                                      'property_account_creditor_price_difference')))
                                    SELECT pt.name       AS product, \
                                           account.name  AS account, \
                                           account.state AS account_state, \
                                           account.code  AS code \
                                    FROM public.product_template AS pt \
                                             LEFT JOIN irpp AS ip ON pt.id = ip.pt_id \
                                             LEFT JOIN account_account AS account ON ip.account_id = account.id
                                    WHERE pt.id in %s \
                                      and account.state = 'total_block'"""

            self.env.cr.execute(product_account_query, (company, products,))
            blocked_product_accounts = self.env.cr.dictfetchall()

            all_blocked_category = blocked_category_accounts + blocked_product_accounts

            line_message = ''
            if all_blocked_category or analytic_accounts:
                for account in all_blocked_category:
                    line_message += _(
                        ' Cuenta: ' + f"{account['account']}" + "\n" + ' Producto: ' + f"{account['product']}" + "\n" + "\n")
                for analytic in analytic_accounts:
                    line_message += _(' Cuenta analítica: ' + f"{analytic['name']}" + "\n" + "\n")
                raise UserError(
                    _("No se puede crear el pedido porque algunas cuentas están totalmente bloqueadas: " + "\n" + "\n" + line_message))
            res = super().button_confirm()
            return res