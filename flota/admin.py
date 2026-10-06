from django.contrib import admin
from .models import Camion, Chofer


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cedula', 'telefono', 'licencia', 'vencimiento_licencia', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'cedula']


@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    list_display = ['matricula', 'marca', 'modelo', 'estado', 'chofer_asignado', 'activo']
    list_filter = ['estado', 'activo']
    search_fields = ['matricula', 'marca']
