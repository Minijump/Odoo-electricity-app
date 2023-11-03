from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #data from contracts
    electricity_contract_id = fields.Many2one('electricity.contract', 
                                              string='Contract')
    price_elec_contract = fields.Monetary(related="electricity_contract_id.price", 
                                          string="Price", 
                                          readonly=True)
    contract_uom = fields.Selection(related='electricity_contract_id.uom')

    #data from bom
    electricity_consumption_from_bom = fields.Float(compute='_compute_electricity_from_bom')
    electricity_cost_from_bom = fields.Monetary(compute='_compute_electricity_from_bom')
    include_in_product_consumption = fields.Boolean()

    #data for product
    additional_consumption = fields.Float()
    electricity_consumption = fields.Float(compute='_compute_elec_consumption')
    electricity_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], 
                                       compute='_compute_default_uom',
                                       store=True,
                                       readonly=False,
                                       string="Uom",
                                       required=True)
    electricity_cost = fields.Monetary(compute="_compute_elec_cost", string="Cost of the elec. consumption")
    cost_with_elec = fields.Monetary(compute="_compute_cost_with_elec", string="Cost of product with electricity")

    def _convert_units(self, source , dest):
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
        if not source or not dest:
                return 1  
        return conversion_factors[(source, dest)]
    
    
    @api.depends('electricity_consumption', 'electricity_uom')  #not working with 'price_elec_contract'???
    def _compute_elec_cost(self):
        for prod in self:
            prod.electricity_cost = (prod.electricity_consumption * 
                                     prod._convert_units(prod.electricity_uom, prod.contract_uom) * 
                                     prod.price_elec_contract)

    @api.depends('electricity_cost', 'standard_price')
    def _compute_cost_with_elec(self):
        for prod in self:
            prod.cost_with_elec = prod.electricity_cost + prod.standard_price 

    @api.depends('electricity_contract_id')
    def _compute_default_uom(self):
        for prod in self:
            prod.electricity_uom = prod.contract_uom or 'kwh'
           
    @api.depends('bom_ids', 'electricity_uom')
    def _compute_electricity_from_bom(self):
        for prod in self:
            electricity_consumption_from_bom, electricity_cost_from_bom = 0, 0
            for line in prod.bom_ids[:1].bom_line_ids:
                electricity_consumption_from_bom += (line.product_id.electricity_consumption * 
                                                     prod._convert_units(line.product_id.electricity_uom, 
                                                                         prod.electricity_uom) * 
                                                     line.product_qty)
                electricity_cost_from_bom += line.product_id.electricity_cost * line.product_qty
                
            prod.electricity_consumption_from_bom = electricity_consumption_from_bom
            prod.electricity_cost_from_bom = electricity_cost_from_bom

    @api.depends('include_in_product_consumption', 
                 'electricity_consumption_from_bom', 
                 'additional_consumption')
    def _compute_elec_consumption(self):
        for prod in self:
            if prod.include_in_product_consumption:
                prod.electricity_consumption = prod.electricity_consumption_from_bom + prod.additional_consumption
            else:
                prod.electricity_consumption = prod.additional_consumption