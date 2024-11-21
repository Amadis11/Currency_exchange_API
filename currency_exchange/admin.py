from django.contrib import admin
from .models import ExchangeRate

class ExchangeRateAdmin(admin.ModelAdmin):

    def formatted_date(self, obj):
        # Use the desired datetime format
        return obj.date.strftime('%Y-%m-%d %H:%M:%S')

    # Add this method to the list_display
    formatted_date.admin_order_field = 'date'  # Allow sorting by datetime
    formatted_date.short_description = 'Date'  # Column title

    list_display = ('currency_from', 'currency_to', 'exchange_rate', 'formatted_date')
    list_filter = ('currency_from', 'currency_to')
    search_fields = ('currency_from', 'currency_to')
    
admin.site.register(ExchangeRate, ExchangeRateAdmin)
