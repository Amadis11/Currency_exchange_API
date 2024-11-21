from django.urls import path
from . import views

urlpatterns = [
    path('currency/', views.currency, name='currency'),  # To list all currencies
    path('currency/<str:currency_from>/<str:currency_to>/', views.currency, name='currency'),  # For specific pairs
]
