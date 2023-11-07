from odoo import api,fields,models

class Device(models.Model):
     _name = "device.consumption.product"
     _description = "Represent electric devices"

     device_id = fields.Many2one('device')
     device_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')],
                                   compute="_compute_device_uom")
    
     product_id = fields.Many2one('product.template', required=True)
     units = fields.Integer()
     energy = fields.Float(compute='_compute_energy')
     
     @api.depends('device_id.uom')
     def _compute_device_uom(self):
          for cons in self:
               cons.device_uom = cons.device_id.uom if cons.device_id.uom else 'wh'

     @api.depends('device_id.uom', 'units', 'product_id')
     def _compute_energy(self):
          for cons in self:
               cons.energy = (cons.units * 
                              cons.product_id.electricity_consumption * 
                              cons.product_id._convert_units(cons.product_id.electricity_uom, cons.device_uom))
     