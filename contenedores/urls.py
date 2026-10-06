from django.urls import path
from . import views

app_name = 'contenedores'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('contenedores/', views.lista_contenedores, name='lista'),
    path('contenedores/nuevo/', views.nuevo_contenedor, name='nuevo'),
    path('contenedores/<int:pk>/', views.detalle_contenedor, name='detalle'),
    path('contenedores/<int:pk>/editar/', views.editar_contenedor, name='editar'),
    path('contenedores/<int:pk>/gastos/agregar/', views.agregar_gasto, name='agregar_gasto'),
    path('contenedores/<int:pk>/permisos/agregar/', views.agregar_permiso, name='agregar_permiso'),
    path('contenedores/<int:pk>/permisos/<int:permiso_pk>/editar/', views.editar_permiso, name='editar_permiso'),
    path('contenedores/<int:pk>/documentos/subir/', views.subir_documento, name='subir_documento'),
    path('importadores/', views.lista_importadores, name='importadores'),
    path('importadores/nuevo/', views.nuevo_importador, name='nuevo_importador'),
]
