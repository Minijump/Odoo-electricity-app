# coding: utf-8
import odoo.tests
from odoo.tests import tagged

@tagged('-at_install', 'post_install')
class ElectricityMrpTest(odoo.tests.TransactionCase):


    def test_mrp_bom_computation(self):
        """
        setup: -add a contract and a consumption to a product
               -create a bom
        action: -add bom consumption to product's consumption
                -change bom values + product values
        tests: -check if consumptions are correct before and after bom is added
               -check values after changes
        """
        #create the first product
        contract = self.env['electricity.contract'].create({
            'name': 'Test Contract 5',
            'price': 0.1,  
            'uom': 'kwh',  
        })
        product = self.env['product.template'].create({
            'name': 'product test 5',
            'standard_price': 10,
            'electricity_uom' : 'wh',
        })
        product.electricity_contract_id = contract.id
        product.additional_consumption = 1000.0
        #create the product which will be used in bom (+ different contract)
        contract_bom = self.env['electricity.contract'].create({
            'name': 'Test Contract 6',
            'price': 2,  
            'uom': 'kwh',  
        })
        product_bom = self.env['product.template'].create({
            'name': 'product test 6',
            'standard_price': 30,
            'electricity_uom' : 'kwh'
        })
        product_bom.electricity_contract_id = contract_bom.id
        product_bom.additional_consumption = 100.0
        #create the bom
        uom_bom = self.env['uom.uom'].create({
                'name': "Hours",
                'category_id': 1,
                'factor': 1,
                'uom_type': "smaller",
            })
        product_product = self.env['product.product'].create({
            'product_tmpl_id': product.id,
            'uom_id': uom_bom.id
        })
        product_product_bom = self.env['product.product'].create({
            'product_tmpl_id': product_bom.id,
            'uom_id': uom_bom.id
        })
        bom = self.env['mrp.bom'].create({
            'product_id': product_product.id,
            'product_tmpl_id': product_product.product_tmpl_id.id,
            'product_qty': 1,
            'type': 'normal',
            'bom_line_ids':[
                (0, 0, {'product_id': product_product_bom.id, 'product_qty': 10})
            ]
        })

        #Test if all values are ok
        self.assertEqual(product.electricity_consumption, 1000, 
                         "Electricity consumption is not correct without bom")
        self.assertEqual(product.electricity_cost, 100, 
                         "Electricity cost is not correct without bom")
        self.assertEqual(product.electricity_consumption_from_bom, 1000, 
                         "Electricity consumption from bom is not correct without bom")
        self.assertEqual(product.electricity_cost_from_bom, 2000, 
                         "Electricity cost from bom is not correct without bom")
        
        #include bom in computation
        product.include_in_product_consumption = True
        #Test if all values are ok
        self.assertEqual(product.electricity_consumption_from_bom, 1000, 
                         "Electricity consumption from bom is not correct after adding bom")
        self.assertEqual(product.electricity_cost_from_bom, 2000, 
                         "Electricity cost from bom is not correct after adding bom")
        self.assertEqual(product.electricity_consumption, 2000, 
                         "Electricity consumption is not correct after adding bom")
        self.assertEqual(product.electricity_cost, 2100, 
                         "Electricity cost is not correct after adding bom")
        
        #change bom values
        #add the same line to bom
        bom.bom_line_ids[:1].product_qty = 20
        bom.bom_line_ids = [
                (0, 0, {'product_id': product_product_bom.id, 'product_qty': 10}),
            ]
        #Test if all values are ok
        self.assertEqual(product.electricity_consumption_from_bom, 3000, 
                         "Electricity consumption from bom is not correct after changing bom (add one line + change first line)")
        self.assertEqual(product.electricity_cost_from_bom, 6000, 
                         "Electricity cost from bom is not correct after changing bom (add one line + change first line)")
        self.assertEqual(product.electricity_consumption, 4000, 
                         "Electricity consumption is not correct after changing bom (add one line + change first line)")
        self.assertEqual(product.electricity_cost, 6100, 
                         "Electricity cost is not correct after changing bom (add one line + change first line)")
        
        #change product's uom
        product.electricity_uom = 'wh'
        #Test if all values are ok
        self.assertEqual(product.electricity_consumption_from_bom, 3000000, 
                         "Electricity consumption from bom is not correct after changing product's uom")
        self.assertEqual(product.electricity_cost_from_bom, 6000, 
                         "Electricity cost from bom is not correct after changing product's uom")
        self.assertEqual(product.electricity_consumption, 3001000, 
                         "Electricity consumption is not correct after changing product's uom")
        self.assertEqual(product.electricity_cost, 6000.1, 
                         "Electricity cost is not correct after changing product's uom")
        
        #change product's additional consumption
        product.additional_consumption = 2000
        #Test if all values are ok
        self.assertEqual(product.electricity_consumption_from_bom, 3000000, 
                         "Electricity consumption from bom is not correct after changing product's additional consumption")
        self.assertEqual(product.electricity_cost_from_bom, 6000, 
                         "Electricity cost from bom is not correct after changing product's additional consumption")
        self.assertEqual(product.electricity_consumption, 3002000, 
                         "Electricity consumption is not correct after changing product's additional consumption")
        self.assertEqual(product.electricity_cost, 6000.2, 
                         "Electricity cost is not correct after changing product's additional consumption")
