from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_product_accounts(self):
        products = []
        for rec in self.order_line:
            products.append(rec.product_id.product_tmpl_id.id)
        products = tuple(products)
        company = str(self.env.company.id)

        query = """
            with irpp as 
            (
                select cast(substring(irp.res_id from '[0-9].*') as int) as pc_id, cast(substring(irp.value_reference from '[0-9].*') as int) as account_id from ir_property as irp
                where irp.name = 'property_stock_valuation_account_id' and irp.company_id = %s
            )
            SELECT pt.name AS product, account.name AS account, account.state AS account_state FROM public.product_template AS pt
            LEFT JOIN product_category AS categ ON pt.categ_id = categ.id
            LEFT JOIN irpp AS ip ON categ.id = ip.pc_id
            LEFT JOIN account_account AS account ON ip.account_id = account.id
            WHERE pt.id in %s and account.state = 'total_block' """
        self.env.cr.execute(query,(company,products,))
        blocked_accounts = self.env.cr.dictfetchall()
        line_message = ''

        if blocked_accounts:
            for account in blocked_accounts:
                line_message += _(' Cuenta: ' + f"{account['account']}" + "\n" + ' Producto: ' + f"{account['product']}"  + "\n" + "\n")
            if self.analytic_account_id.state == 'total_block':
                line_message += _(' Cuenta analítica: '+ self.analytic_account_id.code + ' ' + self.analytic_account_id.name + "\n" + "\n")
            raise UserError(_("No se puede crear el pedido porque algunas cuentas están totalmente bloqueadas: " + "\n" + "\n" + line_message))