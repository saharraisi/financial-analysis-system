from django.db import models
from django.db.models import JSONField

STATUS_CHOICES = (
    ("Sell", "Sell Stock"),
    ("Buy", "Buy Stock"),
    ("Hold", "Hold Stock")
)


class Stock(models.Model):
    stock_symbol = models.CharField(max_length=10, unique=True)
    stock_name = models.CharField(max_length=20)
    status = models.CharField(choices=STATUS_CHOICES, max_length=5, default="Hold")


class StockData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    opening_price = models.DecimalField(max_digits=20, decimal_places=15)
    closing_price = models.DecimalField(max_digits=20, decimal_places=15)
    high = models.DecimalField(max_digits=20, decimal_places=15)
    low = models.DecimalField(max_digits=20, decimal_places=15)
    volume = models.BigIntegerField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.stock.stock_symbol} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class AdditionalData(models.Model):
    data_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    additional_info = JSONField()

    def __str__(self):
        return f"{self.data_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
