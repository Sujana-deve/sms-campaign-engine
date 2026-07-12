from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('campaigns/new/', views.new_campaign, name='new_campaign'),
    path('campaigns/<uuid:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/preview-message/', views.preview_message, name='preview_message'),
    path('contacts/import/', views.import_contacts, name='import_contacts'),
    path('contacts/template/', views.download_template, name='download_template'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/<uuid:contact_id>/toggle/', views.toggle_contact, name='toggle_contact'),
    path('contacts/<uuid:contact_id>/edit/', views.edit_contact, name='edit_contact'),
]