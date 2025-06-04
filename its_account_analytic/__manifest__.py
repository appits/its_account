# -*- coding: utf-8 -*-
{
    'name': "Account group blocking",
    "summary": "Accout group blocking",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",
    'category': 'account',
    'version': '15.0.1.0.0',
    # Any module necessary for this one to work correctly
    'depends': ['base','account', 'analytic'],
    # Always loaded
    'data': [
        # Views
        'views/account_account_views.xml',
        'views/account_analytic_account_views.xml',
    ],
    'license': 'Other proprietary',
}