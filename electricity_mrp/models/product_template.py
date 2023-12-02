from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #data from bom
    electricity_consumption_from_bom = fields.Float(compute='_compute_electricity_from_bom', store=True)
    electricity_cost_from_bom = fields.Monetary(compute='_compute_electricity_from_bom')
    include_in_product_consumption = fields.Boolean()

    #data for product
    additional_consumption = fields.Float()
    electricity_consumption = fields.Float(compute='_compute_elec_consumption')  #overriden
    readonly_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], 
                                     related='electricity_uom')

    @api.depends('bom_ids', 'electricity_uom', 'bom_ids.bom_line_ids')
    def _compute_electricity_from_bom(self):
        """
        Compute the electricity consumption from bom
        """
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
        """
        'electricity_consumption' is now a computed field: bom_consumption + additional_consumption
        """
        for prod in self:
            bom_consumption = prod.electricity_consumption_from_bom if prod.include_in_product_consumption else 0
            prod.electricity_consumption = prod.additional_consumption + bom_consumption

    @api.depends('additional_consumption', 
                 'electricity_uom', 
                 'electricity_cost_from_bom')  # 'price_elec_contract'???
    def _compute_elec_cost(self):
        """
        Override _compute_elec_cost
        Bom cost has to be computed because products in it may have different electricity contracts 
        """
        super()._compute_elec_cost()
        for prod in self:
            bom_cost = prod.electricity_cost_from_bom if prod.include_in_product_consumption else 0
            additional_cost =(prod.additional_consumption * 
                              prod._convert_units(prod.electricity_uom, prod.contract_uom) * 
                              prod.price_elec_contract)
            prod.electricity_cost = additional_cost + bom_cost
