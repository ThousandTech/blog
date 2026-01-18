from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path('info/', views.system_info, name='info'),
    path('state/', views.system_state_details, name='state'),
]
