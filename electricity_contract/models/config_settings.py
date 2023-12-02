from odoo import api, models, fields

class ConfSetting(models.TransientModel):
   _inherit = "res.config.settings"

   #calculator
   power = fields.Float()
   power_uom = fields.Selection(selection=[('w', 'W'), ('kw', 'kW'), ('mw', 'MW')],
                                default='w')
   time = fields.Integer()
   time_uom = fields.Selection(selection=[('s', 'seconds'), ('m','minutes'), ('h', 'hours')],
                               default='h')
   
   energy_uom = fields.Selection(selection=[('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')],
                                default='wh')   
   energy = fields.Float(compute='_compute_energy')

   #product form
   display_in_general_tab = fields.Boolean(string="Display in General Info tab", 
                                           config_parameter='electricity_contract.display_in_general_tab')
   
   #sale order
   use_in_so_line = fields.Boolean(string="Use in sale order line",
                                   config_parameter='electricity_contract.use_in_so_line')

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
