from odoo import api,fields,models

class Device(models.Model):
    _name = "device.consumption"
    _description = "Represent electric devices consumption"

    device_id = fields.Many2one('device')
    device_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')],
                                    compute="_compute_device_uom")
    name = fields.Char()

    duration = fields.Float(required=True)
    power = fields.Float(required=True, string="Power")
    uom = fields.Selection([('w', 'W'), ('kw', 'kW'), ('mw', 'MW')], 
                        default='w',
                        required=True)
    
    energy = fields.Float(compute='_compute_energy')

    def _convert_units_modified(self, source , dest):
        """
        Convert power unit into energy ones
        (from the power uom given by the user, to the energy uom of the device)
        (time measure is given by the user and added while in _compute_energy)
        """
        conversion_factors = {
            ('w', 'wh'): 1,
            ('w', 'kwh'): 0.001,
            ('w', 'mwh'): 1e-6,
            ('kw', 'wh'): 1000,
            ('kw', 'kwh'): 1,
            ('kw', 'mwh'): 0.001,
            ('mw', 'wh'): 1e6,
            ('mw', 'kwh'): 1000,
            ('mw', 'mwh'): 1,
            }
        if not source or not dest:
                return 1  
        return conversion_factors[(source, dest)]
    
    @api.depends('device_id.uom')
    def _compute_device_uom(self):
        """
        Set the uom, linked to device_uom
        """
        for cons in self:
            cons.device_uom = cons.device_id.uom if cons.device_id.uom else 'wh'

    @api.depends('duration', 'power',
                'uom', 'device_id.uom')
    def _compute_energy(self):
        """
        Set the energy consumption: power * duration
        """
        for cons in self:
            cons.energy = (cons.power * 
                           cons._convert_units_modified(cons.uom, cons.device_uom) * 
                           cons.duration)
