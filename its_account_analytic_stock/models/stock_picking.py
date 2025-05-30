from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class StockMove(models.Model):
    _inherit = "stock.move"

    def _block_process_by_accounts(self, vals_list, picking_type):
        products = []
        query_list = []
        i = 0

        for rec in vals_list:
            prd_list = []
            prd_list.append(rec['product_id'])
            prod = tuple(prd_list)
            self._cr.execute('SELECT product_tmpl_id FROM public.product_product WHERE id = %s',prod)
            product_template = int(''.join(map(str,self._cr.fetchone())))
          
            account_analytic_list = []
            account_analytic_list.append(rec['analytic_account_id'])
            account = tuple(account_analytic_list)
            self._cr.execute('SELECT id, name FROM public.account_analytic_account WHERE id = %s',account)
            analytic = self.env.cr.dictfetchall()  
            #analytic_id = int(''.join(map(str,self._cr.fetchone())))

            tuple_to_list = [product_template, analytic[i]['id'], analytic[i]['name']]
            products.append(product_template)
            query_list.append(tuple(tuple_to_list))
            tuple_products = tuple(products)
            i += 1

        company = str(self.env.company.id)

        if company and products:
            create_query = """CREATE TABLE IF NOT EXISTS picking_line_data (product_id int, analytic_account_id int, analytic_account_name text);"""
            self.env.cr.execute(create_query)
            write_query = """INSERT INTO picking_line_data VALUES (%s, %s, %s)"""
            self.env.cr.executemany(write_query, query_list)
            self.env.cr.execute("""SELECT * FROM picking_line_data""")
            picking_line_data_table = self.env.cr.dictfetchall()  # Used to debug
        
        first_query = """ 
            WITH sale_data AS 
            ( 
                SELECT * FROM picking_line_data
            ),
            property_account AS
            (
                SELECT CAST(SUBSTRING(irp.res_id FROM '[0-9].*') as int) as pc_id, CAST(SUBSTRING(irp.value_reference from '[0-9].*') AS int) AS account_id from ir_property AS irp
                WHERE irp.company_id = %s AND 
                (%s = 'incoming' AND irp.name IN ('property_stock_account_input_categ_id', 'property_stock_valuation_account_id')) OR
                (%s = 'outgoing' AND irp.name IN ('property_stock_account_output_categ_id', 'property_stock_valuation_account_id')) OR
                (%s = 'internal' AND irp.name IN ('property_stock_valuation_account_id')) OR
                (%s = 'mrp_operation' AND irp.name IN ('property_stock_account_output_categ_id'))
            )
            SELECT   
                    prod_temp.name                                              AS product,
                    prod_categ.name                                             AS category,
                    accounts.account_id                                         AS stock_valuation_account_id,
                    account.name                                                AS stock_valuation_account_name,
                    account.code                                                AS stock_valuation_account_code,
                    STRING_AGG(accounts.analytic_id::TEXT, ',')                 AS stock_valuation_analytics_accounts,
                    sale.analytic_account_id                                    AS account_analytic_id_in_order_line,
                    sale.analytic_account_name                                  AS account_analytic_name_in_order_line

            FROM public.product_template                        AS prod_temp

                    LEFT JOIN product_category                  AS prod_categ           ON prod_temp.categ_id = prod_categ.id
                    LEFT JOIN property_account                  AS prop_account         ON prod_categ.id = prop_account.pc_id
                    LEFT JOIN account_account                   AS account              ON prop_account.account_id = account.id
                    LEFT JOIN analytic_account_ids_rel          AS accounts             ON account.id = accounts.account_id
                    LEFT JOIN sale_data                         AS sale                 ON prod_temp.id = sale.product_id
                    LEFT JOIN account_analytic_account          AS analytic             ON accounts.analytic_id = analytic.id

            WHERE   
                        prod_temp.id IN %s 
                    AND
                        sale.analytic_account_id IS NOT NULL 
                    AND
                        account.has_analytic_accounts = True
            GROUP BY 
                prod_temp.name,
                prod_categ.name,
                accounts.account_id,
                account.name,
                account.code,
                sale.analytic_account_id,
                sale.analytic_account_name
            """
        
        self.env.cr.execute(first_query,(company,picking_type,picking_type,picking_type,picking_type,tuple_products,))

        lines = self.env.cr.dictfetchall()
        self.env.cr.execute("DROP TABLE picking_line_data")
        line_message = ''
        final_message = ''
        
        for line in lines:
            analytics_accounts = []
            if line.get('stock_valuation_analytics_accounts', False):
                analytics_accounts = [int(id) for id in line['stock_valuation_analytics_accounts'].split(',')]
                if line.get('account_analytic_id_in_order_line', False) not in analytics_accounts:
                    line_message += f"{line['product']}" + '/  ' + f"{line['account_analytic_name_in_order_line']}" + '  /  ' + f"{line['stock_valuation_account_code']}" + ' ' + f"{line['stock_valuation_account_name']}" + "\n"
        final_message += line_message
        if line_message:
            raise UserError(_(final_message))
    

    @api.model_create_multi
    def create(self, vals_list):
        picking = vals_list[0].get('picking_id', False)
        picking_type = self.env['stock.picking'].search([('id','=', picking)]).picking_type_id.code
        self._block_process_by_accounts(vals_list, picking_type)
        res = super().create(vals_list)
        return res