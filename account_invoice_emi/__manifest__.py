# -*- coding: utf-8 -*-

{
    'name': 'Account Invoice EMI',
    'version': '2.0.1',
    'author': 'Xetechs GT',
    'website': 'https://xetechs.com',
    'category': 'Account',
    'summary': 'Account Invoice EMI',
    'description': '''
                        You can create Invoice EMI.
                    ''',
    'depends': ['sale_management', 'account', 'project'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/account_invoice_emi_security.xml',
        'data/auto_create_invoice.xml',
        'data/product_data.xml',
        'security/ir.model.access.csv',
        'views/account_invoice_emi.xml',
        'views/sales_order.xml',
        'views/partner_view.xml',
        'report/reports.xml',
        'report/report_emi_template.xml',
    ]
}
