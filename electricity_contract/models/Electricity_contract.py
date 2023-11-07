from odoo import fields,models

class ElectricityContract(models.Model):
    _name = "electricity.contract"
    _description = "Represent electricity contracts"

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    price = fields.Monetary(required=True, string="Price/Uom")
    product_ids = fields.One2many('product.template', 'electricity_contract_id')
    uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], 
                           default='kwh',
                           required=True)
    device_ids = fields.One2many('device', 'electricity_contract_id')

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The name must be unique.')
    ]
