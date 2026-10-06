from django.urls import path
from . import views

app_name = 'flota'

urlpatterns = [
    path('', views.lista_camiones, name='lista'),
    path('nuevo/', views.nuevo_camion, name='nuevo'),
    path('<int:pk>/', views.detalle_camion, name='detalle'),
    path('choferes/', views.lista_choferes, name='choferes'),
]
