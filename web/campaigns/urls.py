from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard,name = 'dashboard'),
    path('campaigns/new/',views.new_campaign,name = 'new_campaign'),
    path('campaigns/<uuid:campaign_id>/',views.campaign_detail,name = 'campaign_detail'),
    
]