from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #config
    display_in_general_tab = fields.Boolean(compute="_compute_config_settings")

    #data from contracts
    electricity_contract_id = fields.Many2one('electricity.contract', 
                                              string='Contract')
    price_elec_contract = fields.Monetary(related="electricity_contract_id.price", 
                                          string="Price", 
                                          readonly=True)
    contract_uom = fields.Selection(related='electricity_contract_id.uom')

    #data for product
    electricity_consumption = fields.Float()
    electricity_uom = fields.Selection([('wh', 'Wh'), ('kwh', 'kWh'), ('mwh', 'MWh')], 
                                       compute='_compute_default_uom',
                                       store=True,
                                       readonly=False,
                                       string="Uom",
                                       required=True)
    electricity_cost = fields.Monetary(compute="_compute_elec_cost", string="Cost of the elec. consumption")
    cost_with_elec = fields.Monetary(compute="_compute_cost_with_elec", string="Cost of product with electricity")

    def _convert_units(self, source , dest):
        """
        Convert energy units
        """
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
    
    def _compute_config_settings(self):
        """
        Set the field(s) which are set in settings
        """
        for prod in self:
            prod.display_in_general_tab = self.env['ir.config_parameter'].sudo().get_param("electricity_contract.display_in_general_tab")

    @api.depends('electricity_contract_id', 'name')
    def _compute_default_uom(self):
        """
        compute the default uom, based on contract
        depends on name: name is a required field, uom will always be set at creation of a product
        """
        for prod in self:
            prod.electricity_uom = prod.contract_uom or 'kwh'
    
    @api.depends('electricity_consumption', 'electricity_uom', 'price_elec_contract')
    def _compute_elec_cost(self):
        """
        Compute the cost of the electricity consumption
        """
        for prod in self:
            prod.electricity_cost = (prod.electricity_consumption * 
                                     prod._convert_units(prod.electricity_uom, prod.contract_uom) * 
                                     prod.price_elec_contract)

    @api.depends('electricity_cost', 'standard_price')
    def _compute_cost_with_elec(self):
        """
        Compute the cost of the product with the electricity consumption
        """
        for prod in self:
            prod.cost_with_elec = prod.electricity_cost + prod.standard_price 
