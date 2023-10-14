from odoo import fields,models

class ElectricityContract(models.Model):
    _name = "electricity.contract"
    _description = "Represent electricity contracts"

    name = fields.Char(required=True)