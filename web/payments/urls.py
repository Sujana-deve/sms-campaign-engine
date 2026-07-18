from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_payment, name='esewa_initiate'),
    path('success/', views.payment_success, name='esewa_success'),
    path('failure/', views.payment_failure, name='esewa_failure'),
]