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

    ElectricityContractTest.test_add_consumption_to_product = test_add_consumption_to_product
    ElectricityContractTest.test_change_product_uom = test_change_product_uom
    ElectricityContractTest.test_change_on_contract = test_change_on_contract
    ElectricityContractTest.test_device_consumptions = test_device_consumptions
