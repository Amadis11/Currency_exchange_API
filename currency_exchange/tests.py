from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from .models import ExchangeRate
from django.db import IntegrityError
from datetime import datetime


class ExchangeRateModelTest(TestCase):

    def setUp(self):
        # Create an initial exchange rate (EUR -> USD with 1.2 exchange rate)
        self.exchange_rate = ExchangeRate.objects.create(
            currency_from='EUR',
            currency_to='USD',
            exchange_rate=Decimal('1.2'),
            date=datetime(2024, 11, 19, 14, 0)
        )

    def test_save_exchange_rate(self):
        # Ensure the exchange rate has been saved correctly
        self.assertEqual(self.exchange_rate.currency_from, 'EUR')
        self.assertEqual(self.exchange_rate.currency_to, 'USD')
        self.assertEqual(self.exchange_rate.exchange_rate, Decimal('1.2'))

    def test_duplicate_prevention(self):
        # Ensure that a duplicate entry for the same currency pair and date is prevented
        with self.assertRaises(ValueError):
            ExchangeRate.objects.create(
                currency_from='USD',
                currency_to='EUR',
                exchange_rate=Decimal('1.3'),
                date=datetime(2024, 11, 19, 14, 0) # Same date as the first one
            )

    def test_save_inverse_pair(self):
        # Create a new ExchangeRate instance with swapped currency order (USD -> EUR with 2 exchange rate)
        exchange_rate = ExchangeRate.objects.create(
            currency_from='USD',
            currency_to='EUR',
            exchange_rate=Decimal('2'),
            date=datetime(2024, 11, 20, 14, 0)
        )

        # Check that the rate has been saved correctly
        self.assertEqual(exchange_rate.currency_from, 'EUR')
        self.assertEqual(exchange_rate.currency_to, 'USD')
        self.assertEqual(exchange_rate.exchange_rate, Decimal('0.5')) # -> inverted


class CurrencyViewTest(TestCase):
    def setUp(self):
        # Create test exchange rates for different dates and hours
        self.exchange_rate_1 = ExchangeRate.objects.create(
            currency_from='EUR',
            currency_to='USD',
            exchange_rate=Decimal('1.2'),
            date=datetime(2024, 11, 21, 14, 0)
        )
        self.exchange_rate_2 = ExchangeRate.objects.create(
            currency_from='EUR',
            currency_to='USD',
            exchange_rate=Decimal('1.5'),
            date=datetime(2024, 11, 21, 15, 0)
        )
        self.exchange_rate_3 = ExchangeRate.objects.create(
            currency_from='GBP',
            currency_to='PLN',
            exchange_rate=Decimal('5.3'),
            date=datetime(2024, 11, 21, 12, 0)
        )

    def test_fetch_exchange_rate_with_datetime_filter(self):
        response = self.client.get('/currency/EUR/USD/?datetime=2024-11-21 14:00:00')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['exchange_rate'], 1.2)

    def test_fetch_exchange_rate_without_datetime_filter(self):
        response = self.client.get('/currency/EUR/USD/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['exchange_rate'], 1.5)  # Latest exchange rate

    def test_invalid_datetime_format(self):
        response = self.client.get('/currency/EUR/USD/?datetime=2024-11-21 14:00')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid datetime format', response.json()['error'])

    def test_fetch_exchange_rate(self):
        response = self.client.get(reverse('currency', args=['GBP', 'PLN']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('exchange_rate', response.json())

    def test_fetch_inverted_exchange_rate(self):
        response = self.client.get(reverse('currency', args=['PLN', 'GBP']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('exchange_rate', response.json())

    def test_fetch_nonexistent_exchange_rate(self):
        response = self.client.get(reverse('currency', args=['JPY', 'AUD']))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_fetch_currency_pairs(self):
        # Test the `/currency/?pairs=true` endpoint
        response = self.client.get('/currency/?pairs=true')
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected pairs
        expected_pairs = [
            {"pair": "EURUSD"},
            {"pair": "GBPPLN"}
        ]
        self.assertEqual(response.json(), expected_pairs)