# coding: utf-8
import odoo.tests
from odoo.tests import tagged
from odoo.addons.electricity_contract.tests.test_electricity_contract import ElectricityContractTest


# This test should only be executed after all modules have been installed.
@tagged('-at_install', 'post_install')
class ElectricityContractTest(ElectricityContractTest):
        
    def test_add_consumption_to_product(self):
        """
        setup: -add a contract and a consumption to a product
        tests: -check if electricity cost is correct
               -check if cost of product with electricity is correct
               -check if product was added into contract's product
        """
        contract = self.env['electricity.contract'].create({
            'name': 'Test Contract',
            'price': 0.1,  
            'uom': 'kwh',  
        })
        product = self.env['product.template'].create({
            'name': 'product test',
            'standard_price': 10,
            'electricity_uom' : 'wh'
        })
        product.electricity_contract_id = contract.id
        product.additional_consumption = 100.0  

        # Check if electricity cost is correct
        self.assertEqual(product.electricity_cost, 10.0, 
                         "Electricity cost is not correct while adding a contract/consumption") 
        # Check if cost of product with electricity is correct
        self.assertEqual(product.cost_with_elec, product.standard_price + product.electricity_cost, 
                         "Cost of product is not correct while adding a contract/consumption")
        #check if product was added in contract's products
        self.assertTrue(product.id in contract.product_ids.ids, 
                        "product was not added in contract's products")
        
    def test_change_product_uom(self):
        """
        setup: -add a contract and a consumption to a product
        action: -change uom
        tests: -check if electricity cost is correct
        """
        contract = self.env['electricity.contract'].create({
            'name': 'Test Contract 2',
            'price': 0.1,  
            'uom': 'kwh',  
        })
        product = self.env['product.template'].create({
            'name': 'product test 2',
            'standard_price': 10,
            'electricity_uom' : 'wh'
        })
        product.electricity_contract_id = contract.id
        product.additional_consumption = 1000.0

        #change uom
        product.electricity_uom = 'wh'
        # Check if electricity cost is correct
        self.assertEqual(product.electricity_cost, 0.1, 
                         "Electricity cost is not correct while changing uom")
        
    def test_change_on_contract(self):
        """
        setup: -add a contract and a consumption to a product
        action: -change price on contract
        tests: -check if electricity cost is correct
        """
        contract = self.env['electricity.contract'].create({
            'name': 'Test Contract 3',
            'price': 0.1,  
            'uom': 'kwh',  
        })
        product = self.env['product.template'].create({
            'name': 'product test 3',
            'standard_price': 10,
            'electricity_uom' : 'wh'
        })
        product.electricity_contract_id = contract.id
        product.additional_consumption = 1000.0

        #change price
        contract.price = 1
        # Check if electricity cost is correct
        self.assertEqual(product.electricity_cost, 1000, 
                         "Electricity cost is not correct while price on contract")
    
    def test_device_consumptions(self):
        """
        setup: -add a contract and a consumption to a product
               -add a device
        action: -create the 2 types of consumption
                -change the product's consumption/ device uom/ consumption duration
        tests: -check if consumptions' values are correctly set
               -check total consumption of device is correctly set
               -check if consumption is still correct after changes
        """
        contract = self.env['electricity.contract'].create({
            'name': 'Test Contract 4',
            'price': 0.1,  
            'uom': 'kwh',  
        })
        product = self.env['product.template'].create({
            'name': 'product test 4',
            'standard_price': 10,
            'electricity_uom' : 'wh'
        })
        product.electricity_contract_id = contract.id
        product.additional_consumption = 1000.0
        device = self.env['device'].create({
            'name': 'device 1',
            'number_device': 10,
            'uom' : 'kwh',
            'electricity_contract_id': contract.id,
        })

        #create consumptions, and check if computed fields are ok
        consumption = self.env['device.consumption'].create({
            'name': 'cons 1',
            'device_id': device.id,
            'duration': 1,
            'power': 1,
            'uom': 'kw'
        })
        self.assertEqual(consumption.energy, 1, 
                         "Energy not well computed for device consumption")
        consumption_product = self.env['device.consumption.product'].create({
            'device_id': device.id,
            'product_id': product.id,
            'units': 10,
        })
        self.assertEqual(consumption_product.energy, 10000, 
                         "Energy not well computed for device consumption product")
        
        #test total value
        self.assertEqual(device.total_consumption, 100010, 
                         "Total consumption of device not well computed")
        self.assertEqual(device.total_cost, 10001, 
                         "Total consumption'cost of device not well computed")
        
        #test atfter changes in the product's consumption
        product.additional_consumption = 2000.0
        self.assertEqual(device.total_consumption, 200010, 
                         "Total consumption of device not well computed after product's consumption changes")
        self.assertEqual(device.total_cost, 20001, 
                         "Total consumption'cost of device not well computed after product's consumption changes")
        
        #test after change in consumption
        consumption.duration = 2
        self.assertEqual(device.total_consumption, 200020, 
                         "Total consumption of device not well computed after consumption's duration changes")
        self.assertEqual(device.total_cost, 20002, 
                         "Total consumption'cost of device not well computed after consumption's duration changes")
        
        #test after device's uom change
        device.uom = 'wh'
        self.assertEqual(device.total_consumption, 200020000, 
                         "Total consumption of device not well computed after device's uom changes")
        self.assertEqual(device.total_cost, 20002, 
                         "Total consumption'cost of device not well computed after device's uom changes")


    """
    ----------------------------------------------------------------------------------------------------------------------------
    NEW TESTS
    ----------------------------------------------------------------------------------------------------------------------------
    """


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
