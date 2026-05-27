from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('campaigns/new/', views.new_campaign, name='new_campaign'),
    path('campaigns/<uuid:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('contacts/import/', views.import_contacts, name='import_contacts'),
    path('contacts/template/', views.download_template, name='download_template'),
]