from django.contrib import admin
from django.urls import path, include
import campaigns.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(campaigns.urls)),
]