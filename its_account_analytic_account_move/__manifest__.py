# -*- coding: utf-8 -*-
{
    'name': "Account group blocking invoice",
    "summary": "Accout group blocking invoice",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",
    'category': 'account',
    'version': '15.0.1.0.0',
    # Any module necessary for this one to work correctly
    'depends': ['base','account','its_account_analytic'],
    # Always loaded
    'data': [
        'views/account_move_views.xml'
    ],
    'license': 'Other proprietary',
}