from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    electricity_contract_id = fields.Many2one('electricity.contract', 
                                              string='Contract')
    price_elec_contract = fields.Monetary(related="electricity_contract_id.price", 
                                          string="Price", 
                                          readonly=True)
    contract_uom = fields.Selection(related='electricity_contract_id.uom')

    electricity_consumption = fields.Float(string="Consumption")
    electricity_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], 
                                       compute='_compute_default_uom',
                                       store=True,
                                       readonly=False,
                                       string="Uom",)
    convert_units = fields.Float(compute="_compute_conversion")

    electricity_cost = fields.Monetary(compute="_compute_elec_cost", string="Cost of the elec. consumption")
    cost_with_elec = fields.Monetary(compute="_compute_cost_with_elec", string="Cost of product with electricity")

    def _compute_elec_cost(self):
        for rec in self:
            rec.electricity_cost = rec.price_elec_contract * rec.electricity_consumption * rec.convert_units

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
            if not rec.contract_uom or not rec.electricity_uom:
                rec.convert_units = 1
            else:
                key = (rec.electricity_uom, rec.electricity_contract_id.uom)
                rec.convert_units = conversion_factors[key]

    @api.depends('electricity_contract_id')
    def _compute_default_uom(self):
        for rec in self:
            if rec.electricity_contract_id:
                rec.electricity_uom = rec.electricity_contract_id.uom
            else:
                rec.electricity_uom = 'kwh'
           