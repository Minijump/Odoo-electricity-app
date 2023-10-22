# -*- coding: utf-8 -*-

{
    'name': 'Electricity Contract',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'author': "Minijump",
    'application': True,
    'category': 'Uncategorized',
    'summary': 'Create Electricity contract and add electricity consumption to products',
    'description': "Track the electricity consumption of creating your products",
    'image': ['./static/description/banner.gif'],
    'depends': [
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/electricity_contract_views.xml',
        'views/product_template_views.xml',  
    ],
    'price': '37',
    'support': 'ecuyer.duchevalier@gmail.com'
}