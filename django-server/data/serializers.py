from datetime import datetime
import pytz

from django.utils import timezone
from rest_framework import serializers

from .models import Stock, StockData, AdditionalData


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ['stock', 'opening_price', 'closing_price', 'high', 'low', 'volume', 'timestamp']

    def to_internal_value(self, data):
        # Convert Unix timestamp to datetime
        if 'timestamp' in data:
            try:
                unix_timestamp = float(data['timestamp'])
                aware_datetime = timezone.make_aware(datetime.fromtimestamp(unix_timestamp), timezone=pytz.UTC)
                data['timestamp'] = aware_datetime
            except (ValueError, TypeError):
                raise serializers.ValidationError({"timestamp": "Invalid timestamp format."})

        if 'stock_symbol' in data:
            stock_symbol = data.get('stock_symbol')
            try:
                stock = Stock.objects.get(stock_symbol=stock_symbol)
            except Stock.DoesNotExist:
                raise serializers.ValidationError({"stock_symbol": "No stock matches this symbol."})

                # Add the found Stock object to the data dictionary
            data['stock'] = stock.id

            # Remove the stock_symbol key from the data dictionary
            data.pop('stock_symbol', None)

        return super(StockDataSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        representation = super(StockDataSerializer, self).to_representation(instance)
        datetime_str = representation['timestamp']
        datetime_str = datetime_str.replace('Z', '+00:00')
        datetime_obj = datetime.fromisoformat(datetime_str)
        timestamp = datetime_obj.timestamp()
        representation['timestamp'] = timestamp
        representation['stock'] = Stock.objects.get(id=representation['stock']).stock_symbol
        return representation


class AdditionalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalData
        fields = ['data_type', 'timestamp', 'additional_info']

    def to_internal_value(self, data):
        # Extract data_type and timestamp, put the rest in additional_info
        internal_value = {
            'data_type': data.get('data_type'),
            'additional_info': {key: value for key, value in data.items() if key not in ['data_type', 'timestamp']}
        }

        if 'timestamp' in data:
            try:
                unix_timestamp = float(data['timestamp'])
                aware_datetime = timezone.make_aware(datetime.fromtimestamp(unix_timestamp), timezone=pytz.UTC)
                internal_value['timestamp'] = aware_datetime
            except (ValueError, TypeError):
                raise serializers.ValidationError({"timestamp": "Invalid timestamp format."})

        return super().to_internal_value(internal_value)

    def to_representation(self, instance):
        # Merge additional_info with data_type and timestamp for outgoing data
        representation = super().to_representation(instance)
        additional_info = representation.pop('additional_info', {})
        for key, value in additional_info.items():
            representation[key] = value
        return representation
