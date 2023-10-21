from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    electricity_contract_id = fields.Many2one('electricity.contract', string='Contract')
    price_elec = fields.Monetary(related="electricity_contract_id.price", string="Price of a kWh", readonly=True)
    electricity_consumption = fields.Float(string="Consumption (kWh)")
    electricity_cost = fields.Monetary(compute="_compute_elec_cost", string="Cost of the elec. consumption")
    cost_with_elec = fields.Monetary(compute="_compute_cost_with_elec", string="Cost of product with electricity")

    def _compute_elec_cost(self):
        for rec in self:
            rec.electricity_cost = rec.price_elec * rec.electricity_consumption

    def _compute_cost_with_elec(self):
        for rec in self:
            rec.cost_with_elec = rec.electricity_cost + rec.standard_price 
