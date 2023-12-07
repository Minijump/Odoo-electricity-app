# -*- coding: utf-8 -*-

{
    'name': 'Electricity Management',
    'version': '17.0.1.0.0',
    'license': 'OPL-1',
    'author': "Minijump",
    'application': True,
    'category': 'Sales Management',
    'summary': 'Create Electricity contract and add electricity consumption to products',
    'description': "Track the electricity consumption of creating your products",
    'images': ['./static/description/banner.png'],
    'depends': [
        'sale',
        'sale_margin'
    ],
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/electricity_contract_views.xml',
        'views/product_template_views.xml', 
        'views/config_setting_electricity_contract_views.xml',
        'views/device_views.xml' 
    ],
    'price': '87.65',
    'support': 'ecuyer.duchevalier@gmail.com'
}
