from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('actualizar/<int:pk>/', views.actualizar_tracking, name='actualizar'),
    path('json/<int:pk>/', views.tracking_json, name='json'),
]
