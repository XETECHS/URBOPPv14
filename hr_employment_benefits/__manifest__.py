#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR employment benefits',
    'category': 'Human Resources',
    'sequence': 1,
    'summary': 'Manage the employment benefits to you employees in odoo',
    'author': "Luis Aquino --> laquino@xetechs.com",
    'maintainer': "Xetechs, S.A.",
    'description': "",
    'depends': [
        'hr_payroll',
        'hr_payroll_account',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',
        'views/hr_employment_benefits_view.xml',
    ],
}
