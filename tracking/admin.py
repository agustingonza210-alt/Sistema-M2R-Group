from django.contrib import admin
from .models import TrackingSnapshot


@admin.register(TrackingSnapshot)
class TrackingSnapshotAdmin(admin.ModelAdmin):
    list_display = ['contenedor_numero', 'fuente', 'exitoso', 'consultado_en']
    list_filter = ['fuente', 'exitoso']
    readonly_fields = ['consultado_en']
