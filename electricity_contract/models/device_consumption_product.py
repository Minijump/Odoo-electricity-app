from odoo import api,fields,models

class Device(models.Model):
     _name = "device.consumption.product"
     _description = "Represent electric devices consumption linked to a product"
     _sql_constraints = [
        ("check_positive_product_number", "CHECK(units >= 0)", "The number of units must be greater or equal to 0"),
    ]

     device_id = fields.Many2one('device')
     device_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')],
                                   compute="_compute_device_uom")
    
     product_id = fields.Many2one('product.template', required=True)
     units = fields.Integer()
     energy = fields.Float(compute='_compute_energy')
     
     @api.depends('device_id.uom')
     def _compute_device_uom(self):
          """
          Set the uom, linked to device_uom
          """
          for cons in self:
               cons.device_uom = cons.device_id.uom if cons.device_id.uom else 'wh'

     @api.depends('device_id.uom', 'units', 'product_id',
                  'product_id.electricity_consumption', 'product_id.electricity_uom')
     def _compute_energy(self):
          """
          Set the energy consumption: #products created * consumption for this product
          """
          for cons in self:
               cons.energy = (cons.units * 
                              cons.product_id.electricity_consumption * 
                              cons.product_id._convert_units(cons.product_id.electricity_uom, cons.device_uom))
     