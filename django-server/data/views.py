from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_eventstream import send_event

from .models import Stock, StockData
from .serializers import AdditionalDataSerializer, StockDataSerializer, StockSerializer
from .utils import send_to_kafka


class DataIngestView(APIView):
    def post(self, request, format=None):
        data = request.data.copy()
        if 'data_type' in data:
            # Handle AdditionalData
            topic = "additional_data"
            serializer = AdditionalDataSerializer(data=data)
        else:
            # Handle StockData
            topic = "stock_data"
            serializer = StockDataSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            send_to_kafka(topic, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockDataRetrieveView(APIView):
    def get(self, request, format=None):
        stock_symbol = request.query_params.get('stock_symbol')

        if stock_symbol:
            queryset = StockData.objects.filter(stock__stock_symbol=stock_symbol)
        else:
            queryset = StockData.objects.all()

        serializer = StockDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StockRetrieveView(APIView):
    def get(self, request):
        stock_list = Stock.objects.all()
        serializer = StockSerializer(stock_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def view_chart(request):
    return render(request, 'data/index.html')


def change_stock_status(request):
    try:
        stock_symbol = request.GET.get('stock_symbol')
        sma = request.GET.get('sma')
        ema = request.GET.get('ema')
        rsi = request.GET.get('rsi')
        action = request.GET.get('action')
        stock = Stock.objects.get(stock_symbol=stock_symbol)

        stock.status = action
        stock.save()
        send_event(
            'notification',
            'stock_status_changed',
            {'stock_symbol': stock_symbol, 'sma': sma, 'ema': ema, 'rsi':rsi, 'status': action}
        )
        return HttpResponse('stock updated', status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return HttpResponse('bad request', status=status.HTTP_400_BAD_REQUEST)
