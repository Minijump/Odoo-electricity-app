import base64
import io
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import seaborn as sns
import pandas as pd
import textwrap

from odoo import _, api, models, fields
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #data from bom
    electricity_consumption_from_bom = fields.Float(compute='_compute_electricity_from_bom', store=True)
    electricity_cost_from_bom = fields.Monetary(compute='_compute_electricity_from_bom', compute_sudo=True)
    include_in_product_consumption = fields.Boolean()

    #data for product
    additional_consumption = fields.Float()
    electricity_consumption = fields.Float(compute='_compute_elec_consumption')  #overriden
    readonly_uom = fields.Selection(related='electricity_uom')

    #data for report
    bar_graph = fields.Binary()

    @api.depends('bom_ids', 'electricity_uom', 'bom_ids.bom_line_ids')
    def _compute_electricity_from_bom(self):
        """
        Compute the electricity consumption from bom
        """
        for prod in self:
            electricity_consumption_from_bom, electricity_cost_from_bom = 0, 0
            for line in prod.bom_ids[:1].bom_line_ids:
                electricity_consumption_from_bom += (line.product_id.electricity_consumption * 
                                                     prod._convert_units(line.product_id.electricity_uom, 
                                                                         prod.electricity_uom) * 
                                                     line.product_qty)
                electricity_cost_from_bom += line.product_id.electricity_cost * line.product_qty
                
            prod.electricity_consumption_from_bom = electricity_consumption_from_bom
            prod.electricity_cost_from_bom = electricity_cost_from_bom

    @api.depends('include_in_product_consumption', 
                 'electricity_consumption_from_bom', 
                 'additional_consumption')
    def _compute_elec_consumption(self):
        """
        'electricity_consumption' is now a computed field: bom_consumption + additional_consumption
        """
        for prod in self:
            bom_consumption = prod.electricity_consumption_from_bom if prod.include_in_product_consumption else 0
            prod.electricity_consumption = prod.additional_consumption + bom_consumption

    @api.depends('additional_consumption', 
                 'electricity_uom', 
                 'electricity_cost_from_bom')  # 'price_elec_contract'???
    def _compute_elec_cost(self):
        """
        Override _compute_elec_cost
        Bom cost has to be computed because products in it may have different electricity contracts 
        """
        super()._compute_elec_cost()
        for prod in self:
            bom_cost = prod.electricity_cost_from_bom if prod.include_in_product_consumption else 0
            additional_cost =(prod.additional_consumption * 
                              prod._convert_units(prod.electricity_uom, prod.contract_uom) * 
                              prod.price_elec_contract)
            prod.electricity_cost = additional_cost + bom_cost

    def _get_bom_components_rec(self, target_uom, bom_products=[], level=''):
        """
        Return a list with the products' infos present in the bom
        Used in the report
        """
        for line in self.bom_ids[:1].bom_line_ids:
            # total consumptions of product
            product_dic = {}
            product_dic['level'] = level
            product_dic['prod'] = line.product_tmpl_id
            uom_conv = line.product_tmpl_id._convert_units(line.product_tmpl_id.electricity_uom , target_uom)
            product_dic['cons'] = line.product_tmpl_id.electricity_consumption * uom_conv
            product_dic['qty'] = line.product_qty
            product_dic['contract'] = line.product_tmpl_id.electricity_contract_id
            product_dic['cost'] = line.product_tmpl_id.electricity_cost * product_dic['qty']
            product_dic['add_in_graph'] = True
            bom_products.append(product_dic)

            if product_dic['prod'].include_in_product_consumption:
                bom_products[-1]['add_in_graph'] = False 

                #add the consumptions from bom
                product_dic['prod']._get_bom_components_rec(target_uom, bom_products, level.replace('|', '-') + '|')

                #additional consumptions of the product
                uom_conv = line.product_tmpl_id._convert_units(line.product_tmpl_id.electricity_uom , target_uom)
                add_cons_dic = {}
                add_cons_dic['level'] = level.replace('|', '-') + '|'
                add_cons_dic['prod'] = False 
                add_cons_dic['prod_add_cons'] = product_dic['prod']
                uom_conv = line.product_tmpl_id._convert_units(line.product_tmpl_id.electricity_uom , target_uom)
                add_cons_dic['cons'] = line.product_tmpl_id.additional_consumption * uom_conv
                add_cons_dic['qty'] = 1.0
                add_cons_dic['contract'] = line.product_tmpl_id.electricity_contract_id
                add_cons_dic['cost'] = line.product_tmpl_id.additional_consumption * line.product_tmpl_id.price_elec_contract #qty always 1
                add_cons_dic['add_in_graph'] = True
                bom_products.append(add_cons_dic)
            
    def _get_elec_detail(self, target_uom):
        """
        Return a list with the detailled electricity consumption of the product
        Used in the report
        """
        for prod in self.filtered('include_in_product_consumption'):
            bom_products=[]
            level=''

            #consumptions of bom products
            prod._get_bom_components_rec(target_uom, bom_products, level)

            #additional consumption of Main product
            this_add_cons_dic = {}
            this_add_cons_dic['level'] = ''
            this_add_cons_dic['prod'] = False 
            this_add_cons_dic['prod_add_cons'] = prod
            this_add_cons_dic['cons'] = prod.additional_consumption 
            this_add_cons_dic['qty'] = 1.0
            this_add_cons_dic['contract'] = prod.electricity_contract_id
            this_add_cons_dic['cost'] = prod.additional_consumption * prod.price_elec_contract
            this_add_cons_dic['add_in_graph'] = True
            bom_products.append(this_add_cons_dic)
            
            prod._compute_graph(bom_products)
            return bom_products
                
    def _compute_graph(self, bom_products):
        """
        Generate the graphs for the report
        """
        # Extract 'prod' and 'cons' from bom_products
        data = []
        to_display = [item for item in bom_products if item['cost'] > 0 and item['add_in_graph'] == True]
        for item in to_display:
            label = (item['prod'].name if item['prod'] 
                     else item['prod_add_cons'].name + "'s add. cons.")
            data.append({'label': label, 'cost': item['cost']})

        # Convert the data list to a DataFrame
        df = pd.DataFrame(data)
        df = df.groupby('label').sum().reset_index()
        df = df.sort_values(by='cost', ascending=False)

        # Create a horizontal bar plot 
        sns.set(style="whitegrid")
        plt.figure(figsize=(11, 10))
        ax = sns.barplot(x='cost', y='label', data=df, orient='h')

        # Wrap long labels
        ax.set_yticklabels([textwrap.fill(label, width=15) for label in df['label']], fontsize=10)
        # Annotate the axis 
        currency = self.currency_id.symbol
        ax.set_title('Your Electricity Cost Composition', fontsize=14)
        ax.set_xlabel('Cost (' + currency + ')', fontsize=12)
        ax.set_ylabel('')
        # Annotates bars
        for p in ax.patches:
            ax.annotate(f'{p.get_width():,.2f}' + ' ' + currency, 
                        (p.get_width(), p.get_y() + p.get_height() / 2), 
                        ha='left', va='center', xytext=(8, 0), textcoords='offset points')

        # Save the graph to a BytesIO object
        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        plt.close()

        # Save the image to the binary field
        self.write({'bar_graph': base64.b64encode(image_stream.getvalue())})
