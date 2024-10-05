from odoo import api, models, fields

class ConfSetting(models.TransientModel):
   _inherit = "res.config.settings"

   #product form custo
   display_in_general_tab = fields.Boolean(string="Display in General Info tab", 
                                           config_parameter='electricity_contract.display_in_general_tab')
   
   #sale order line custo
   use_in_so_line = fields.Boolean(string="Use in sale order line",
                                   config_parameter='electricity_contract.use_in_so_line')
