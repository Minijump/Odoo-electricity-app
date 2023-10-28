from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    electricity_contract_id = fields.Many2one('electricity.contract', string='Contract')
    price_elec = fields.Monetary(related="electricity_contract_id.price", string="Price of a kWh", readonly=True)
    electricity_consumption = fields.Float(string="Consumption (kWh)")
    electricity_cost = fields.Monetary(compute="_compute_elec_cost", string="Cost of the elec. consumption")
    cost_with_elec = fields.Monetary(compute="_compute_cost_with_elec", string="Cost of product with electricity")
    electricity_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], 
                                       default='electricity_contract_id.uom')
    convert_units = fields.Float(compute="_compute_conversion")
    
    def _compute_elec_cost(self):
        for rec in self:
            rec.electricity_cost = rec.price_elec * rec.electricity_consumption * rec.convert_units

    def _compute_cost_with_elec(self):
        for rec in self:
            rec.cost_with_elec = rec.electricity_cost + rec.standard_price 

    def _compute_conversion(self):
        conversion_factors = {
            ('wh', 'wh'): 1,
            ('wh', 'kwh'): 0.001,
            ('wh', 'mwh'): 1e-6,
            ('kwh', 'wh'): 1000,
            ('kwh', 'kwh'): 1,
            ('kwh', 'mwh'): 0.001,
            ('mwh', 'wh'): 1e6,
            ('mwh', 'kwh'): 1000,
            ('mwh', 'mwh'): 1,
            }

        for rec in self:
            key = (rec.electricity_uom, rec.electricity_contract_id.uom)
            rec.convert_units = conversion_factors[key]
           
            
