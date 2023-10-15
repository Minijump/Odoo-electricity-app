# -*- coding: utf-8 -*-

{
    'name': 'Electricity Contract',
    'version': '1.0',
    'author': "Minijump",
    'application': True,
    'category': 'Uncategorized',
    'summary': 'Create Electricity contract',
    'description': "Create Electricity contract",
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/electricity_contract_views.xml',  
    ],
}