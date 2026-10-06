from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime


class Importador(models.Model):
    nombre = models.CharField(max_length=200)
    ruc = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'Importadores'

    def __str__(self):
        return self.nombre


class Contenedor(models.Model):
    ESTADO_CHOICES = [
        ('en_transito', 'En Tránsito'),
        ('aduana_uy', 'Aduana UY'),
        ('aduana_py', 'Aduana PY'),
        ('terminal', 'En Terminal'),
        ('liberado', 'Liberado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    TIPO_CHOICES = [
        ('20DV', "20' Dry Van"),
        ('40DV', "40' Dry Van"),
        ('40HC', "40' High Cube"),
        ('20RF', "20' Reefer"),
        ('40RF', "40' Reefer"),
        ('20OT', "20' Open Top"),
        ('40OT', "40' Open Top"),
    ]

    # Identificación
    numero = models.CharField(max_length=20, unique=True, help_text='Ej: MSCU1234567')
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES, default='40HC')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_transito')

    # Datos navieros
    bl_numero = models.CharField(max_length=50, verbose_name='Número BL', blank=True)
    booking = models.CharField(max_length=50, blank=True)
    naviera = models.CharField(max_length=100, blank=True)
    navio = models.CharField(max_length=100, blank=True, verbose_name='Nave/Buque')
    puerto_origen = models.CharField(max_length=100, blank=True)
    puerto_destino = models.CharField(max_length=100, default='Puerto de Asunción')

    # Fechas clave
    eta = models.DateField(null=True, blank=True, verbose_name='ETA (estimada)')
    fecha_llegada = models.DateField(null=True, blank=True, verbose_name='Fecha real de llegada')
    ultimo_dia_libre = models.DateField(null=True, blank=True, verbose_name='Último día libre')
    fecha_liberacion = models.DateField(null=True, blank=True, verbose_name='Fecha de liberación')
    fecha_entrega = models.DateField(null=True, blank=True, verbose_name='Fecha de entrega')

    # Relaciones
    importador = models.ForeignKey(
        Importador, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='contenedores'
    )
    camion = models.ForeignKey(
        'flota.Camion', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='contenedores'
    )
    responsable = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='contenedores_asignados'
    )

    # Descripción de carga
    descripcion_carga = models.TextField(blank=True)
    ncm = models.CharField(max_length=20, blank=True, verbose_name='Código NCM', help_text='Nomenclatura Común del MERCOSUR')
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Peso bruto (kg)')
    valor_cif_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Valor CIF (USD)')

    # Meta
    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contenedores_creados')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name_plural = 'Contenedores'

    def __str__(self):
        return f'{self.numero} — {self.get_estado_display()}'

    @property
    def dias_libres_restantes(self):
        if not self.ultimo_dia_libre:
            return None
        hoy = timezone.now().date()
        delta = (self.ultimo_dia_libre - hoy).days
        return delta

    @property
    def semaforo_demurrage(self):
        dias = self.dias_libres_restantes
        if dias is None:
            return 'sin_dato'
        if self.estado in ('entregado', 'cancelado'):
            return 'entregado'
        if dias > 3:
            return 'verde'
        if dias >= 0:
            return 'amarillo'
        return 'rojo'

    @property
    def dias_demurrage_acumulados(self):
        if not self.ultimo_dia_libre:
            return 0
        hoy = timezone.now().date()
        if self.estado == 'entregado' and self.fecha_entrega:
            referencia = self.fecha_entrega
        else:
            referencia = hoy
        delta = (referencia - self.ultimo_dia_libre).days
        return max(0, delta)

    @property
    def total_gastos_usd(self):
        return self.gastos.filter(moneda='USD').aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')

    @property
    def total_gastos_pgs(self):
        return self.gastos.filter(moneda='PGS').aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')


class Gasto(models.Model):
    CATEGORIA_CHOICES = [
        ('flete', 'Flete internacional'),
        ('thc', 'THC (Terminal Handling)'),
        ('almacenaje', 'Almacenaje'),
        ('aduana', 'Despacho aduanero'),
        ('arancel', 'Arancel MERCOSUR'),
        ('iva', 'IVA importación'),
        ('tasa_aduana', 'Tasa aduanera'),
        ('transporte', 'Transporte interno'),
        ('despachante', 'Honorarios despachante'),
        ('seguro', 'Seguro'),
        ('permiso', 'Permiso regulatorio'),
        ('demurrage', 'Demurrage'),
        ('otro', 'Otro'),
    ]

    MONEDA_CHOICES = [('USD', 'USD'), ('PGS', 'Guaraníes')]
    TIPO_CHOICES = [('presupuestado', 'Presupuestado'), ('real', 'Real')]

    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name='gastos')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descripcion = models.CharField(max_length=200, blank=True)
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='USD')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='real')
    fecha = models.DateField(default=datetime.date.today)
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    notas = models.CharField(max_length=300, blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = 'Gastos'

    def __str__(self):
        return f'{self.get_categoria_display()} — {self.moneda} {self.monto}'


class Permiso(models.Model):
    ORGANISMO_CHOICES = [
        ('SENAVE', 'SENAVE (Servicio Nacional de Calidad Vegetal)'),
        ('INAN', 'INAN (Instituto Nacional de Alimentación y Nutrición)'),
        ('DINAVISA', 'DINAVISA (Dirección de Vigilancia Sanitaria)'),
        ('SENACSA', 'SENACSA (Servicio Nacional de Calidad y Salud Animal)'),
        ('DNA', 'DNA (Dirección Nacional de Aduanas)'),
        ('MADES', 'MADES (Ministerio Ambiente)'),
        ('OTRO', 'Otro organismo'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_tramite', 'En Trámite'),
        ('aprobado', 'Aprobado'),
        ('observado', 'Observado'),
        ('rechazado', 'Rechazado'),
    ]

    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name='permisos')
    organismo = models.CharField(max_length=10, choices=ORGANISMO_CHOICES)
    numero_expediente = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateField(null=True, blank=True)
    fecha_aprobacion = models.DateField(null=True, blank=True)
    plazo_dias = models.IntegerField(null=True, blank=True, help_text='Plazo estimado en días hábiles')
    observaciones = models.TextField(blank=True)
    documento = models.FileField(upload_to='permisos/', null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['organismo']
        verbose_name_plural = 'Permisos'

    def __str__(self):
        return f'{self.organismo} — {self.get_estado_display()}'

    @property
    def bloquea_despacho(self):
        return self.estado in ('pendiente', 'en_tramite', 'observado', 'rechazado')


class Documento(models.Model):
    TIPO_CHOICES = [
        ('bl', 'Bill of Lading (BL)'),
        ('factura', 'Factura Comercial'),
        ('packing', 'Packing List'),
        ('dad', 'Declaración Aduanera (DAD)'),
        ('certificado_origen', 'Certificado de Origen'),
        ('seguro', 'Póliza de Seguro'),
        ('otro', 'Otro'),
    ]

    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documentos/')
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subido_en = models.DateTimeField(auto_now_add=True)
    notas = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['-subido_en']
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.nombre}'


class EventoTimeline(models.Model):
    TIPO_CHOICES = [
        ('estado', 'Cambio de estado'),
        ('tracking', 'Actualización de tracking'),
        ('permiso', 'Permiso'),
        ('gasto', 'Gasto registrado'),
        ('documento', 'Documento agregado'),
        ('nota', 'Nota'),
        ('alerta', 'Alerta'),
    ]

    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name='eventos')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    automatico = models.BooleanField(default=False, help_text='Generado por el sistema')

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Eventos de Timeline'

    def __str__(self):
        return f'{self.contenedor.numero} — {self.titulo}'
