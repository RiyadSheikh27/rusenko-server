from .views import *
from django.urls import path

urlpatterns = [
    path('reviews/', ReviewAPIView.as_view(), name='reviews'),
    path('our-results/', OurResultsAPIView.as_view(), name='our-results'),
    path('request-quote/', RequestQuoteAPIView.as_view(), name='request-quote'),
]