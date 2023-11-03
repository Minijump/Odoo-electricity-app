# -*- coding: utf-8 -*-

{
    'name': 'Electricity Management: MRP extension',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'author': "Minijump",
    'application': True,
    'category': 'Manufacturing',
    'summary': 'Extends electricity management module to add mrp features',
    'description': "Compute electricity consumption from BOM, add additional consumption, ...",
    #'images': ['./static/description/banner.png'],
    'depends': [
        'electricity_contract',
        'mrp'
    ],
    'data': [
        'views/product_template_views.xml'
    ],
    'support': 'ecuyer.duchevalier@gmail.com'
}