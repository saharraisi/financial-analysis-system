from django.db.models.signals import post_save
from django.dispatch import receiver
from django_eventstream import send_event

from .models import StockData
from .serializers import StockDataSerializer


@receiver(post_save, sender=StockData)
def post_save_handler(sender, instance, created, **kwargs):
    if created:
        data = StockDataSerializer(instance=instance).data
        send_event(
            f'stock-{instance.stock.stock_symbol}',
            'stock_updated',
            dict(data)
        )
