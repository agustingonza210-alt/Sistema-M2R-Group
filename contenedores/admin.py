from django.contrib import admin
from .models import Contenedor, Gasto, Permiso, Documento, EventoTimeline, Importador


@admin.register(Importador)
class ImportadorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ruc', 'telefono', 'email', 'activo']
    search_fields = ['nombre', 'ruc']
    list_filter = ['activo']


class GastoInline(admin.TabularInline):
    model = Gasto
    extra = 0
    fields = ['categoria', 'monto', 'moneda', 'tipo', 'fecha']


class PermisoInline(admin.TabularInline):
    model = Permiso
    extra = 0
    fields = ['organismo', 'estado', 'fecha_solicitud', 'fecha_aprobacion']


@admin.register(Contenedor)
class ContenedorAdmin(admin.ModelAdmin):
    list_display = ['numero', 'tipo', 'estado', 'importador', 'eta', 'ultimo_dia_libre', 'camion']
    list_filter = ['estado', 'tipo', 'naviera']
    search_fields = ['numero', 'bl_numero', 'navio', 'importador__nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
    inlines = [GastoInline, PermisoInline]
    date_hierarchy = 'creado_en'


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['contenedor', 'categoria', 'monto', 'moneda', 'tipo', 'fecha']
    list_filter = ['categoria', 'moneda', 'tipo']


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ['contenedor', 'organismo', 'estado', 'fecha_solicitud', 'fecha_aprobacion']
    list_filter = ['organismo', 'estado']


@admin.register(EventoTimeline)
class EventoTimelineAdmin(admin.ModelAdmin):
    list_display = ['contenedor', 'tipo', 'titulo', 'timestamp', 'usuario']
    list_filter = ['tipo']
    readonly_fields = ['timestamp']
