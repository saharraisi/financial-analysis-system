from django.contrib import admin

from .models import AdditionalData, StockData, Stock

admin.site.register(AdditionalData)
admin.site.register(StockData)
admin.site.register(Stock)
