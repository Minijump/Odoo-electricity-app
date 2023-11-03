from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #data from bom
    electricity_consumption_from_bom = fields.Float(compute='_compute_electricity_from_bom')
    electricity_cost_from_bom = fields.Monetary(compute='_compute_electricity_from_bom')
    include_in_product_consumption = fields.Boolean()

    #data for product
    additional_consumption = fields.Float()
    electricity_consumption = fields.Float(compute='_compute_elec_consumption')

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