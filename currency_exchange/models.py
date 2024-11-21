from django.db import models
from decimal import Decimal


class ExchangeRate(models.Model):
    currency_from = models.CharField(max_length=3)  # e.g., 'GBP'
    currency_to = models.CharField(max_length=3)  # e.g., 'PLN'
    exchange_rate = models.DecimalField(max_digits=25, decimal_places=10)  # e.g., 5.000000
    date = models.DateTimeField()

    class Meta:
        unique_together = ('currency_from', 'currency_to', 'date')

    def save(self, *args, **kwargs):
        # Enforce alphabetical ordering of currency codes
        if self.currency_from > self.currency_to:
            self.currency_from, self.currency_to = self.currency_to, self.currency_from
            self.exchange_rate = Decimal('1.0') / self.exchange_rate  # Adjust the exchange_rate to match the inverted order

        # Check for duplicate currency pair for the same date
        if ExchangeRate.objects.filter(currency_from=self.currency_from, currency_to=self.currency_to, date=self.date).exists():
            raise ValueError("This currency pair (or its inverse) already exists.")

        super().save(*args, **kwargs)
