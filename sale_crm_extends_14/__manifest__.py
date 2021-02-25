# -*- coding: utf-8 -*-
{
    'name': "Sale CRM Extends and Other Fields",

    'author': "XETECHS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts', 'crm', 'utm', 'sale_management','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/lead_views.xml',
        'views/sale_views.xml',
    ],
}