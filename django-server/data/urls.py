from django.urls import path, include

from .views import DataIngestView, StockDataRetrieveView, view_chart, StockRetrieveView, change_stock_status

app_name = 'data'

urlpatterns = [
    path('ingest/', DataIngestView.as_view(), name='ingest'),
    path('stock-data/', StockDataRetrieveView.as_view(), name='stock-data-retrieve'),
    path('view-chart/', view_chart, name='view'),
    path('view-chart/<str:stock_symbol>/', view_chart, name='view-chart'),
    path('stock-list/', StockRetrieveView.as_view(), name='stock-list'),
    path('stock-status-update/',change_stock_status, name='stock-status')
]
