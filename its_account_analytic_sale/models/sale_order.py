from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _block_process_by_accounts(self, final_message):   
        if self.analytic_account_id:
            products = []
            query_list = []
            i = 0
            for line in self.order_line:
                if line.product_id:
                    products.append(line.product_id.product_tmpl_id.id)
                    tuple_to_list = [products[i]]
                    query_list.append(tuple(tuple_to_list))
                    i += 1
            products = tuple(products)
            company = str(self.env.company.id)

            if company and products:
                create_query = """CREATE TABLE IF NOT EXISTS sale_line_data (product_id int );"""
                self.env.cr.execute(create_query)
                write_query = """INSERT INTO sale_line_data VALUES (%s)"""
                self.env.cr.executemany(write_query, query_list)
                self.env.cr.execute("""SELECT * FROM sale_line_data""")
                sale_line_data_table = self.env.cr.dictfetchall()  # Used to debug

                first_query = """ 
                WITH sale_data AS 
                ( 
                    SELECT * FROM sale_line_data
                ),
                property_account AS
                (
                    SELECT  
                        CAST(SUBSTRING(irp.res_id FROM '[0-9].*') AS int) AS pc_id, 
                        CAST(SUBSTRING(irp.value_reference FROM '[0-9].*') AS int) AS account_id 
                    FROM ir_property AS irp
                    WHERE irp.company_id = %s AND irp.name = 'property_stock_valuation_account_id'
                )

                SELECT   
                        prod_temp.name                                              AS product,
                        prod_categ.name                                             AS category,
                        accounts.account_id                                         AS stock_valuation_account_id,
                        account.name                                                AS stock_valuation_account_name,
                        account.code                                                AS stock_valuation_account_code,
                        STRING_AGG(accounts.analytic_id::TEXT, ',')                 AS stock_valuation_analytics_accounts

                FROM public.product_template                        AS prod_temp

                        LEFT JOIN product_category                  AS prod_categ           ON prod_temp.categ_id = prod_categ.id
                        LEFT JOIN property_account                  AS prop_account         ON prod_categ.id = prop_account.pc_id
                        LEFT JOIN account_account                   AS account              ON prop_account.account_id = account.id
                        LEFT JOIN analytic_account_ids_rel          AS accounts             ON account.id = accounts.account_id

                WHERE   
                            prod_temp.id IN %s 
                GROUP BY 
                    prod_temp.name,
                    prod_categ.name,
                    accounts.account_id,
                    account.name,
                    account.code
                """
                self.env.cr.execute(first_query,(company,products,))
                lines = self.env.cr.dictfetchall()
                self.env.cr.execute("DROP TABLE sale_line_data")

                line_message = ''
                for line in lines:
                    analytics_accounts = []
                    if line.get('stock_valuation_analytics_accounts', False):
                        analytics_accounts = [int(id) for id in line['stock_valuation_analytics_accounts'].split(',')]
                        if self.analytic_account_id.id not in analytics_accounts:
                            line_message += f"{line['product']}" + '/  ' +  f"{line['stock_valuation_account_code']}" + ' ' + f"{line['stock_valuation_account_name']}" + "\n"
                final_message += line_message
                if line_message:
                    raise UserError(_(final_message))   
        return True 

    @api.constrains('order_line','analytic_account_id')
    def _check_product_accounts(self):
        final_message = """No se puede crear/editar la orden de venta: """'\n' + """La cuenta analítica """  + f"{self.analytic_account_id.name}" + """  no se encuentra en los grupos de cuentas asignadas a las cuentas contables dentro de las categorías de los siguientes productos: """ '\n' + '\n'
        self._block_process_by_accounts(final_message)

    def action_confirm(self):
        final_message = """No se puede confirmar la orden de venta: """'\n' + """La cuenta analítica """  + f"{self.analytic_account_id.name}" + """  no se encuentra en los grupos de cuentas asignadas a las cuentas contables dentro de las categorías de los siguientes productos: """ '\n' + '\n'
        self._block_process_by_accounts(final_message)
        res = super().action_confirm()
        return res