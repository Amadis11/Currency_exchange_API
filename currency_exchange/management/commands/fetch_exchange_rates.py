from django.core.management.base import BaseCommand  # Import BaseCommand
import yfinance as yf
from decimal import Decimal
from datetime import datetime
from currency_exchange.models import ExchangeRate


class Command(BaseCommand):
    help = 'Fetches exchange rates from Yahoo Finance and saves to the database'

    def handle(self, *args, **kwargs):
        # List of currency pairs to fetch
        currency_pairs = [
            'EURUSD=X', 'USDJPY=X', 'PLNUSD=X', 'GBPPLN=X', 'GBPUSD=X',
            'EURPLN=X', 'EURJPY=X', 'GBPJPY=X', 'NOKPLN=X', 'NOKUSD=X',
            'UAHUSD=X'
        ]

        start_date = '2024-08-01'
        interval = '1h'

        # Iterate through each currency pair
        for pair in currency_pairs:
            # Fetch historical data for each currency pair
            forex_data = yf.download(pair, start=start_date, interval=interval)

            # Iterate over the data and save it to the database
            for index, row in forex_data.iterrows():
                date = index.strftime('%Y-%m-%d %H:%M:%S')  # Convert index to string
                rate = row['Close'][pair] if pair in row['Close'] else None
                exchange_rate_decimal = Decimal(str(rate))
                # Save the exchange rate to the database
                exchange_rate_entry = ExchangeRate(
                    currency_from=pair[:3],  # First 3 characters of the pair
                    currency_to=pair[3:6],   # Last 3 characters of the pair
                    exchange_rate=exchange_rate_decimal,
                    date=date  # Date from the index
                )
                exchange_rate_entry.save()

        self.stdout.write(self.style.SUCCESS("Exchange rates have been fetched and saved successfully!"))
