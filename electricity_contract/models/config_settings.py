from odoo import api, models, fields

class ConfSetting(models.TransientModel):
   _inherit = "res.config.settings"

   power = fields.Float()
   power_uom = fields.Selection(selection=[('w', 'W'), ('kw', 'kW'), ('mw', 'MW')],
                                default='w')
   time = fields.Integer()
   time_uom = fields.Selection(selection=[('s', 'seconds'), ('m','minutes'), ('h', 'hours')],
                               default='h')
   
   energy_uom = fields.Selection(selection=[('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')],
                                default='wh')   
   energy = fields.Float(compute='_compute_energy')

   @api.depends('power', 'power_uom', 'time', 'time_uom', 'energy_uom')
   def _compute_energy(self):
      uom_factors = {'w': 1, 
                     'kw': 1000, 
                     'mw': 1000000, 
                     's': 1/3600, 
                     'm': 1/60, 
                     'h': 1,
                     'wh': 1,
                     'kwh': 1/1000,
                     'mwh': 1/1000000
                     }
      for rec in self:
         energy_wh = (rec.power * uom_factors[rec.power_uom]) * (rec.time * uom_factors[rec.time_uom])
         rec.energy = energy_wh * uom_factors[rec.energy_uom]

