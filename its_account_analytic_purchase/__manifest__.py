# -*- coding: utf-8 -*-
{
    'name': "Account group blocking purchase",
    "summary": "Accout group blocking purchase",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",
    'category': 'purchase',
    'version': '15.0.1.0.0',
    # Any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'its_account_analytic'],
    # Always loaded
    'data': [
        # Views
        'views/purchase_order_views.xml'
    ],
    'license': 'Other proprietary',
}