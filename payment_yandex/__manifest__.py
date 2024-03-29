# -*- coding: utf-8 -*-

{
		"name": "Yandex Checkout",
		"summary": "Yandex Checkout",
		"description": """
		Install dependencies:
		`pip3 install yandex_checkout`
	""",
		"category": "Accounting/Payment",
		"version": "1.0.1",
		'author': "eSwap",
		"sequence": 1,
		'license': 'OPL-1',
		"depends": ['payment'],
		"data": [
				'views/yandex_templates.xml',
				'views/payment_views.xml',
				'data/payment_acquirer_data.xml',
				],
		'images': ['static/description/banner.png','static/description/icon.png'],
		'installable': True,
		'post_init_hook': 'create_missing_journal_for_acquirers',
		'uninstall_hook': 'uninstall_hook',
		"external_dependencies": {
				"python": [
						"yandex_checkout"
						],
				},
		"support": "odoo@eswap.ch",
		"price": 100,
		"currency": "EUR",
		}
