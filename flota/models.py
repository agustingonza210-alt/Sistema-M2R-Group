from django.db import models
from django.contrib.auth.models import User


class Camion(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_ruta', 'En Ruta'),
        ('mantenimiento', 'En Mantenimiento'),
        ('inactivo', 'Inactivo'),
    ]

    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula/Chapa')
    marca = models.CharField(max_length=50, blank=True)
    modelo = models.CharField(max_length=50, blank=True)
    anio = models.IntegerField(null=True, blank=True, verbose_name='Año')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='disponible')
    chofer_asignado = models.ForeignKey(
        'Chofer', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='camion_asignado'
    )
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['matricula']
        verbose_name_plural = 'Camiones'

    def __str__(self):
        return f'{self.matricula} — {self.marca} {self.modelo}'

    @property
    def contenedores_activos(self):
        return self.contenedores.exclude(estado__in=['entregado', 'cancelado']).count()


class Chofer(models.Model):
    nombre = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20, blank=True, verbose_name='Cédula de identidad')
    telefono = models.CharField(max_length=30, blank=True)
    licencia = models.CharField(max_length=50, blank=True, verbose_name='Número de licencia')
    vencimiento_licencia = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'Choferes'

    def __str__(self):
        return self.nombre
