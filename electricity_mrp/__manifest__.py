# -*- coding: utf-8 -*-

{
    'name': 'FREE MRP extension: Electricity Management',
    'version': '16.0.2.0.1',
    'license': 'OPL-1',
    'author': "Minijump",
    'application': True,
    'category': 'Manufacturing',
    'summary': 'Extends electricity management module to add mrp features',
    'description': "Compute electricity consumption from BOM, add additional consumption, ...",
    'images': ['./static/description/banner.png'],
    'depends': [
        'electricity_contract',
        'mrp'
    ],
    'data': [
        'views/product_template_views.xml',
        'reports/product_consumption_report.xml',
    ],
    'support': 'ecuyer.duchevalier@gmail.com'
}
