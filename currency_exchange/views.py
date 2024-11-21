from django.http import JsonResponse
from .models import ExchangeRate
from django.db.models import Q
from decimal import Decimal, ROUND_DOWN
from datetime import datetime


def currency(request, currency_from=None, currency_to=None):
    # Check for pairs filter parameter
    pairs_filter = request.GET.get('pairs', None)

    if not currency_from and not currency_to:
        if pairs_filter == 'true':
            # Fetch distinct currency pairs from both currency_from and currency_to
            pairs = (
                ExchangeRate.objects
                .values('currency_from', 'currency_to')
                .distinct()
            )

            # Return a list of currency pairs in the format {"pair": "PLNUSD"}
            response_data = [{"pair": f"{pair['currency_from']}{pair['currency_to']}"} for pair in pairs]
        else:
            # Fetch distinct currency codes from both fields and combine them
            currency_from_list = ExchangeRate.objects.values_list('currency_from', flat=True).distinct()
            currency_to_list = ExchangeRate.objects.values_list('currency_to', flat=True).distinct()

            # Combine the two lists and remove duplicates
            unique_currencies = sorted(set(currency_from_list) | set(currency_to_list))

            # Create the JSON response
            response_data = [{"code": code} for code in unique_currencies]

        return JsonResponse(response_data, safe=False)

    elif currency_from and currency_to:
        # Case 2: Both arguments are provided, return the newest exchange rate or inverted rate
        # Retrieve datetime parameter if provided
        date_param = request.GET.get('datetime', None)

        if date_param:
            try:
                # Attempt to parse the datetime (ensure it matches the required format)
                filter_datetime = datetime.strptime(date_param, '%Y-%m-%d %H:00:00')
            except ValueError:
                return JsonResponse({'error': 'Invalid datetime format. Use YYYY-MM-DD HH:00:00.'}, status=400)

            # Filter the exchange rates by datetime if the parameter is provided
            exchange_rate = (
                ExchangeRate.objects
                .filter(
                    Q(currency_from=currency_from, currency_to=currency_to) |
                    Q(currency_from=currency_to, currency_to=currency_from),
                    date=filter_datetime
                )
                .first()
            )
        else:
            # If no datetime is provided, get the latest exchange rate
            exchange_rate = (
                ExchangeRate.objects
                .filter(
                    Q(currency_from=currency_from, currency_to=currency_to) |
                    Q(currency_from=currency_to, currency_to=currency_from)
                )
                .order_by('-date')  # Order by datetime, newest first
                .first()
            )

        if exchange_rate:
            # Determine if the result is inverted
            is_inverted = exchange_rate.currency_from == currency_to

            # Get the original precision from the database
            original_rate = Decimal(exchange_rate.exchange_rate)
            precision = abs(original_rate.as_tuple().exponent)

            # Calculate the exchange rate with the same precision
            exchange_rate_value = (
                (Decimal(1) / original_rate).quantize(Decimal(f"1.{'0' * precision}"), rounding=ROUND_DOWN)
                if is_inverted
                else original_rate
            )

            response_data = {
                "currency_pair": f"{currency_from}/{currency_to}",
                "exchange_rate": float(exchange_rate_value)  # Convert back to float for JSON serialization
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({"error": "Exchange rate not found."}, status=404)
