from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    # TODO arreglar
    def action_confirm(self):

        mp_products = []
        products = []
        for rec in self.move_raw_ids:
            mp_products.append(rec.product_id.product_tmpl_id.id)

        for rec in self.move_byproduct_ids:
            products.append(rec.product_id.product_tmpl_id.id)

        products = tuple(products)
        mp_products = tuple(mp_products)

        company = str(self.env.company.id)
        if products:
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

            query_mp = """
                with irpp as 
                (
                    select cast(substring(irp.res_id from '[0-9].*') as int) as pc_id, cast(substring(irp.value_reference from '[0-9].*') as int) as account_id from ir_property as irp
                    where irp.name in ('property_stock_valuation_account_id','property_stock_account_consumption_fabrication_categ_id') and irp.company_id = %s
                )
                SELECT pt.name AS product, account.name AS account, account.state AS account_state FROM public.product_template AS pt
                LEFT JOIN product_category AS categ ON pt.categ_id = categ.id
                LEFT JOIN irpp AS ip ON categ.id = ip.pc_id
                LEFT JOIN account_account AS account ON ip.account_id = account.id
                WHERE pt.id in %s and account.state = 'total_block' """ 
            
            self.env.cr.execute(query_mp,(company,mp_products,))

            blocked_mp_accounts = self.env.cr.dictfetchall()

            all_blocked_accounts = blocked_accounts + blocked_mp_accounts
            line_message = ''
            blocked_adjust_account = 'Cuentas en ajustes bloqueadas: ' + "\n"
            if self.env.company.cost_account_prd_labor.state == 'total_block':
                blocked_adjust_account += f"{self.env.company.cost_account_prd_labor.name}" + "\n" 
            if self.env.company.cost_account_prd_factory_load.state == 'total_block':
                blocked_adjust_account += f"{self.env.company.cost_account_prd_factory_load.name}" + "\n" 
            if all_blocked_accounts:
                for account in all_blocked_accounts:
                    line_message += _(' Cuenta: ' + f"{account['account']}" + "\n" + ' Producto: ' + f"{account['product']}"  + "\n" + "\n") 
                if self.env.company.cost_account_prd_factory_load.state == 'total_block' or self.env.company.cost_account_prd_factory_load.state == 'total_block':
                    line_message += blocked_adjust_account
                raise UserError(_("No se puede crear el pedido porque algunas cuentas están totalmente bloqueadas: " + "\n" + "\n" + line_message))
        res = super().action_confirm()
        return res