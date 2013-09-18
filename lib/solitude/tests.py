import json

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

import mock
from nose.tools import eq_

from lib.solitude.api import client, SellerNotConfigured
from lib.solitude.errors import ERROR_STRINGS
from lib.solitude.mock_api import MockSlumber


class SolitudeAPITest(TestCase):

    def setUp(self):
        self.uuid = 'dat:uuid'
        self.pin = '1234'
        client.slumber = MockSlumber()
        client.create_buyer(self.uuid, self.pin)

    def test_get_buyer(self):
        buyer = client.get_buyer(self.uuid)
        eq_(buyer.get('uuid'), self.uuid)
        assert buyer.get('pin')
        assert buyer.get('id') is not None

    def test_non_existent_get_buyer(self):
        buyer = client.get_buyer('something that does not exist')
        assert not buyer

    def test_create_buyer_bubbles_errors_up(self):
        client.slumber.generic.buyer.post.side_effect = None
        client.slumber.generic.buyer.post.return_value = {'errors': 'failure'}
        buyer = client.create_buyer(self.uuid, self.pin)
        assert buyer.get('errors')
        eq_(buyer['errors'], 'failure')

    def test_confirm_pin_with_good_pin(self):
        client.slumber.generic.confirm_pin.post.return_value = {
            'confirmed': True
        }
        assert client.confirm_pin(self.uuid, self.pin)

    def test_confirm_pin_with_bad_pin(self):
        client.slumber.generic.confirm_pin.post.return_value = {
            'confirmed': False
        }
        assert not client.confirm_pin(self.uuid, self.pin[::-1])

    def test_verify_pin_with_good_pin(self):
        client.slumber.generic.verify_pin.post.return_value = {'valid': True}
        assert client.verify_pin(self.uuid, self.pin)['valid']

    def test_verify_pin_with_bad_pin(self):
        client.slumber.generic.verify_pin.post.return_value = {'valid': False}
        assert not client.verify_pin(self.uuid, self.pin)['valid']


class CreateBangoTest(TestCase):
    uuid = 'some:pin'
    seller = {'bango': {'seller': 's', 'resource_uri': 'r',
                        'package_id': '1234'},
              'resource_pk': 'foo'}

    def test_create_no_bango(self):
        with self.assertRaises(ValueError):
            client.create_product('ext:id', None,
                                  {'bango': None, 'resource_pk': 'foo'})

    @mock.patch('lib.solitude.api.client.slumber')
    def test_create_bango(self, slumber):
        # Temporary mocking. Remove when this is mocked properly.
        slumber.bango.generic.post.return_value = {'product': 'some:uri'}
        slumber.bango.product.post.return_value = {'resource_uri': 'some:uri',
                                                   'bango_id': '5678'}
        assert client.create_product('ext:id', 'product:name', self.seller)
        assert slumber.generic.product.post.called
        kw = slumber.generic.product.post.call_args[0][0]
        eq_(kw['external_id'], 'ext:id')
        eq_(slumber.bango.rating.post.call_count, 2)
        assert slumber.bango.premium.post.called

    @mock.patch('lib.solitude.api.client.slumber')
    def test_no_seller(self, slumber):
        slumber.generic.seller.get_object.side_effect = ObjectDoesNotExist
        with self.assertRaises(SellerNotConfigured):
            client.configure_product_for_billing(*range(0, 10))

    @mock.patch('lib.solitude.api.client.slumber')
    def test_no_bango(self, slumber):
        slumber.generic.seller.get_object.return_value = self.seller
        slumber.bango.billing.post.return_value = {
            'billingConfigurationId': 'bar'}
        slumber.bango.product.get_object.side_effect = ObjectDoesNotExist
        eq_(client.configure_product_for_billing(*range(0, 10)), ('bar', 'foo'))

    @mock.patch('lib.solitude.api.client.slumber')
    def test_has_bango(self, slumber):
        slumber.generic.seller.get_object.return_value = self.seller
        slumber.bango.billing.post.return_value = {
            'billingConfigurationId': 'bar'}
        slumber.bango.product.get_object.return_value = {'resource_uri': 'foo'}
        eq_(client.configure_product_for_billing(*range(0, 10)), ('bar', 'foo'))


@mock.patch('lib.solitude.api.client.slumber')
class TransactionTest(TestCase):

    def test_notes_transactions(self, slumber):
        slumber.generic.transaction.get_object.return_value = {
                'notes': json.dumps({'foo': 'bar'})
        }
        trans = client.get_transaction('x')
        eq_(trans['notes'], {'foo': 'bar'})
