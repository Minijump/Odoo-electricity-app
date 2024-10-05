# coding: utf-8
from odoo.fields import Command
import odoo.tests
from odoo.tests import tagged


@tagged('-at_install', 'post_install')
class ElectricityContractTest(odoo.tests.TransactionCase):

    @classmethod
    def setUpClass(cls):
        """
        Set a product a contract, and an electricity consumprtion
        """
        super().setUpClass()
        cls.contract = cls.env['electricity.contract'].create({
            'name': 'Test Contract',
            'price': 0.1,  
            'uom': 'kwh',  
        })
        cls.product = cls.env['product.template'].create({
            'name': 'product test',
            'standard_price': 10,
            'electricity_uom' : 'wh'
        })
        cls.product.electricity_contract_id = cls.contract.id
        cls.product.electricity_consumption = 1000.0  
        
    def test_add_consumption_to_product(self):
        """
        setup: -change electricity consumption
        tests: -check if electricity cost is correct
               -check if cost of product with electricity is correct
               -check if product was added into contract's product
        """
        contract = self.contract
        product = self.product
        product.electricity_consumption = 100.0  
        # Check if electricity cost is correct
        self.assertEqual(product.electricity_cost, 10.0, 
                         "Electricity cost is not correct while adding a contract/consumption") 
        # Check if cost of product with electricity is correct
        self.assertEqual(product.cost_with_elec, 20, 
                         "Cost of product is not correct while adding a contract/consumption")
        #check if product was added in contract's products
        self.assertTrue(product.id in contract.product_ids.ids, 
                        "product was not added in contract's products")
        
    def test_change_product_uom(self):
        """
        action: -change uom
        tests: -check if electricity cost is correct
        """
        product = self.product

        #change uom
        product.electricity_uom = 'wh'
        # Check if electricity cost is correct
        self.assertEqual(product.electricity_cost, 0.1, 
                         "Electricity cost is not correct while changing uom")
        
    def test_change_on_contract(self):
        """
        action: -change price on contract
        tests: -check if electricity cost is correct
        """
        contract = self.contract
        product = self.product

        #change price
        contract.price = 1
        # Check if electricity cost is correct
        self.assertEqual(product.electricity_cost, 1000, 
                         "Electricity cost is not correct while price on contract")
        
    def test_elec_on_so_line(self):
        """
        setup: - create an so
        action: -check bool in settings
        tests: -check that the price include electricity after boolean is checked
        """
        product = self.product

        uom = self.env['uom.uom'].create({
                'name': "Hours",
                'category_id': 1,
                'factor': 1,
                'uom_type': "smaller",
            })
        product_product = self.env['product.product'].create({
            'product_tmpl_id': product.id,
            'uom_id': uom.id,
        })
        product.standard_price = 10 #create product_product override it
        partner = self.env['res.partner'].create({
                    'is_company': False,
                    'name': 'partner_name',
                    'email': 'email_from',
                })
        so  = self.env['sale.order'].create({
            'partner_id': partner.id,
        })

        #boolean = True
        self.env['ir.config_parameter'].sudo().set_param("electricity_contract.use_in_so_line", True)
        #create so line
        so.order_line=[
             Command.create({
                    'product_id': product_product.id,
                    'product_uom_qty': 5.0,
                }),
        ]
        #check price
        self.assertEqual(so.order_line[0].purchase_price, 110, 
                            "Purchase price on so line is not correct after 'add elec' boolean is checked")     
