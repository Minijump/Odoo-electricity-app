# -*- coding: utf-8 -*-

{
    'name': 'Electricity Management',
    'version': '16.0.2.0.0',
    'license': 'LGPL-3',
    'author': "Minijump",
    'application': True,
    'category': 'Uncategorized',
    'summary': 'Create Electricity contract and add electricity consumption to products',
    'description': "Track the electricity consumption of creating your products",
    'images': ['./static/description/banner.png'],
    'depends': [
        'sale',
        'mrp'
    ],
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/electricity_contract_views.xml',
        'views/product_template_views.xml', 
        'views/config_setting_electricity_contract_views.xml' 
    ],
    'price': '37',
    'support': 'ecuyer.duchevalier@gmail.com'
}