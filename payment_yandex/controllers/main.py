# -*- coding: utf-8 -*-
import logging
import werkzeug
from odoo import http
from odoo.http import request
import ipaddress

_logger = logging.getLogger(__name__)

WHITE_LIST_IPS = [
		"185.71.76.0/27",
		"185.71.77.0/27",
		"77.75.153.0/25",
		"77.75.154.128/25",
		"2a02:5180:0:1509::/64",
		"2a02:5180:0:2655::/64",
		"2a02:5180:0:1533::/64",
		"2a02:5180:0:2669::/64",
		]


class YandexController(http.Controller):
	@http.route(['/payment/yandex-checkout/notification_url'], type = 'json', method = ['POST'], auth = 'public',
	            csrf = False)
	def yandex_notification_url(self, **kwargs):
		ip = request.httprequest.remote_addr
		ip_is_in_whitelist = any([ipaddress.ip_address(ip) in ipaddress.ip_network(white_network)
		                          for white_network in WHITE_LIST_IPS])

		if ip_is_in_whitelist:
			request_body = http.request.jsonrequest

			if request_body and request_body.get('type', '') == 'notification':
				request.env['payment.transaction'].sudo().form_feedback(request_body['object'], 'yandex')

		return werkzeug.utils.redirect('/payment/process')

	@http.route(['/payment/yandex-checkout/confirmation_url'], type = 'http', method = ['POST'], auth = 'none',
	            csrf = False)
	def yandex_confirmation_url(self, **kwargs):
		if kwargs.get("yandex_confirmation_url"):
			return werkzeug.utils.redirect(kwargs['yandex_confirmation_url'])
		return werkzeug.utils.redirect('/payment/process')
