from odoo import api,fields,models

class Device(models.Model):
    _name = "device"
    _description = "Represent electric devices"
    _sql_constraints = [
        ("check_positive_device_number", "CHECK(number_device > 0)", "The number of device must be strictly positive"),
    ]


    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    name = fields.Char()
    number_device = fields.Integer(default=1)
    uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], 
                           compute='_compute_default_uom',
                           required=True,
                           readonly=False,
                           store=True)
    readonly_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], related='uom')
    electricity_contract_id = fields.Many2one('electricity.contract', string='Contract', required=True)
    contract_price = fields.Monetary(related='electricity_contract_id.price')
    contract_uom = fields.Selection(related='electricity_contract_id.uom')

    device_consumption_ids = fields.One2many('device.consumption', 'device_id')
    device_consumption_product_ids = fields.One2many('device.consumption.product', 'device_id')

    total_consumption = fields.Float(compute='_compute_consumption')
    total_cost = fields.Float(compute='_compute_cost')

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
    
    @api.depends('electricity_contract_id')
    def _compute_default_uom(self):
        for device in self:
            device.uom = device.electricity_contract_id.uom or 'kwh'
    
    @api.depends('device_consumption_ids', 
                 'device_consumption_product_ids', 
                 'uom',
                 'number_device')
    def _compute_consumption(self):
        for device in self:
            device.total_consumption =(device.number_device*
                                       (sum(device.device_consumption_ids.mapped('energy')) +
                                       sum(device.device_consumption_product_ids.mapped('energy')))
                                       )
            
    @api.depends('total_consumption', 'electricity_contract_id')
    def _compute_cost(self):
        for device in self:
             device.total_cost = (device.total_consumption * device.electricity_contract_id.price * 
                                  device._convert_units(device.uom,device.electricity_contract_id.uom))
             