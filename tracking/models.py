from django.db import models
from django.utils import timezone


class TrackingSnapshot(models.Model):
    """Guarda cada respuesta de las APIs de tracking para historial."""
    FUENTE_CHOICES = [('shipsgo', 'ShipsGo'), ('terminal49', 'Terminal49')]

    contenedor_numero = models.CharField(max_length=20, db_index=True)
    fuente = models.CharField(max_length=15, choices=FUENTE_CHOICES)
    datos_raw = models.JSONField()
    consultado_en = models.DateTimeField(default=timezone.now)
    exitoso = models.BooleanField(default=True)

    class Meta:
        ordering = ['-consultado_en']
        verbose_name_plural = 'Tracking Snapshots'

    def __str__(self):
        return f'{self.contenedor_numero} ({self.fuente}) — {self.consultado_en:%d/%m/%Y %H:%M}'
