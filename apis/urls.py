from django.urls import path
from . import view as api_views

urlpatterns = [
    path('upload_pdfs', api_views.upload_pdfs, name='upload_pdfs'),
    path('indicators', api_views.get_indicators, name='indicators'),
    path('add_indicators', api_views.add_indicators, name='add_indicators'),
    path('calculate', api_views.calculate, name='calculate'),
]
