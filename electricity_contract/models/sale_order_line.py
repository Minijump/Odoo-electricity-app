from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
            

    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
    def _compute_purchase_price(self):
        """
        Override _compute_purchase_price, if use_in_so_line is set in settings:
        use price with elec in so lines
        """
        res = super()._compute_purchase_price()
        if self.env['ir.config_parameter'].sudo().get_param("electricity_contract.use_in_so_line"):
            for line in self:
                line.purchase_price = line.product_id.cost_with_elec
