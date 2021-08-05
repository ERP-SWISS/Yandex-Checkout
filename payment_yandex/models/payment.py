# coding: utf-8
import uuid

from odoo import api, fields, models, _
from odoo.http import request
from odoo.addons.payment.models.payment_acquirer import ValidationError
from yandex_checkout import Configuration, Payment
from werkzeug import urls
import logging

_logger = logging.getLogger(__name__)


class YandexAcquirer(models.Model):
	_inherit = 'payment.acquirer'

	provider = fields.Selection(selection_add = [('yandex', 'Yandex Checkout')], ondelete={'yandex': 'set default'})
	yandex_shop_id = fields.Char(required_if_provider = 'yandex', groups = 'base.group_user', help = "Account ID")
	yandex_secret_key = fields.Char(required_if_provider = 'yandex', groups = 'base.group_user', help = "Secret Key")

	def _get_providers(self):
		providers = super(YandexAcquirer, self)._get_providers()
		providers.append([('yandex', 'Yandex Checkout')])
		return providers

	def _get_yandex_urls(self):
		return urls.url_join(self.get_base_url(), "/payment/yandex-checkout/confirmation_url")

	def yandex_form_generate_values(self, values):
		self.ensure_one()
		base_url = self.get_base_url()
		Configuration.account_id = self.yandex_shop_id
		Configuration.secret_key = self.yandex_secret_key

		tx_values = dict(values)

		from_currency = tx_values['currency']
		to_currency = self.env['res.currency'].sudo().search([('name', '=', 'RUB')], limit = 1)

		try:
			order = request.website.sale_get_order()
		except:
			order = self.env['sale.order'].sudo().browse(request.jsonrequest['params']['order_id'])

		amount = from_currency._convert(tx_values['amount'],
		                                to_currency,
		                                order.company_id,
		                                fields.Date.today()
		                                )

		payment = Payment.create({
				"amount": {
						"value": amount,
						"currency": "RUB"
						},
				"confirmation": {
						"type": "redirect",
						"return_url": urls.url_join(base_url, '/payment/process')
						},
				"capture": True,
				"description": tx_values['reference'],
				}, uuid.uuid4())

		tx_values.update({
				"yandex_confirmation_url": payment.confirmation.confirmation_url,
				"description": tx_values['reference'],
				"amount": amount,
				})

		return tx_values

	def yandex_get_form_action_url(self):
		return self._get_yandex_urls()


class PaymentTransactionYandexCheckout(models.Model):
	_inherit = 'payment.transaction'

	@api.model
	def _yandex_form_get_tx_from_data(self, data):
		reference = data.get('description')

		if not reference:
			error_msg = _('Yandex: received data with missing reference (%s)') % reference
			_logger.info(error_msg)
			raise ValidationError(error_msg)

		txs = self.env['payment.transaction'].search([('reference', '=', reference)])

		if not txs or len(txs) > 1:
			error_msg = 'Yandex: received data for reference %s' % (reference)
			if not txs:
				error_msg += '; no order found'
			else:
				error_msg += '; multiple order found'
			_logger.info(error_msg)
			raise ValidationError(error_msg)
		return txs[0]

	def _yandex_form_validate(self, data):
		status = data.get('status')

		result = self.write({
				'acquirer_reference': data.get('yandex'),
				'date': fields.Datetime.now(),
				})

		if status == 'succeeded':
			self._set_transaction_done()
		elif status in ('pending', 'waiting_for_capture'):
			self._set_transaction_pending()
		else:
			self._set_transaction_cancel()
		return result
