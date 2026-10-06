from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import Contenedor, Gasto, Permiso, Documento, EventoTimeline, Importador


class ContenedorForm(forms.ModelForm):
    class Meta:
        model = Contenedor
        fields = [
            'numero', 'tipo', 'estado',
            'bl_numero', 'booking', 'naviera', 'navio',
            'puerto_origen', 'puerto_destino',
            'eta', 'fecha_llegada', 'ultimo_dia_libre', 'fecha_liberacion', 'fecha_entrega',
            'importador', 'camion', 'responsable',
            'descripcion_carga', 'ncm', 'peso_kg', 'valor_cif_usd',
            'notas',
        ]
        widgets = {
            'eta': forms.DateInput(attrs={'type': 'date'}),
            'fecha_llegada': forms.DateInput(attrs={'type': 'date'}),
            'ultimo_dia_libre': forms.DateInput(attrs={'type': 'date'}),
            'fecha_liberacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'descripcion_carga': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 3}),
            'numero': forms.TextInput(attrs={'placeholder': 'Ej: MSCU1234567', 'class': 'text-uppercase'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="fw-semibold text-muted mb-3 mt-2">Identificación</h6>'),
            Row(
                Column('numero', css_class='col-md-4'),
                Column('tipo', css_class='col-md-3'),
                Column('estado', css_class='col-md-5'),
            ),
            HTML('<h6 class="fw-semibold text-muted mb-3 mt-3">Datos Navieros</h6>'),
            Row(
                Column('bl_numero', css_class='col-md-4'),
                Column('booking', css_class='col-md-4'),
                Column('naviera', css_class='col-md-4'),
            ),
            Row(
                Column('navio', css_class='col-md-6'),
                Column('puerto_origen', css_class='col-md-3'),
                Column('puerto_destino', css_class='col-md-3'),
            ),
            HTML('<h6 class="fw-semibold text-muted mb-3 mt-3">Fechas Clave</h6>'),
            Row(
                Column('eta', css_class='col-md-4'),
                Column('fecha_llegada', css_class='col-md-4'),
                Column('ultimo_dia_libre', css_class='col-md-4'),
            ),
            Row(
                Column('fecha_liberacion', css_class='col-md-4'),
                Column('fecha_entrega', css_class='col-md-4'),
            ),
            HTML('<h6 class="fw-semibold text-muted mb-3 mt-3">Asignaciones</h6>'),
            Row(
                Column('importador', css_class='col-md-4'),
                Column('camion', css_class='col-md-4'),
                Column('responsable', css_class='col-md-4'),
            ),
            HTML('<h6 class="fw-semibold text-muted mb-3 mt-3">Carga y Valores</h6>'),
            Row(
                Column('ncm', css_class='col-md-3'),
                Column('peso_kg', css_class='col-md-3'),
                Column('valor_cif_usd', css_class='col-md-3'),
            ),
            'descripcion_carga',
            'notas',
            Submit('submit', 'Guardar', css_class='btn btn-primary mt-3'),
        )


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['categoria', 'descripcion', 'monto', 'moneda', 'tipo', 'fecha', 'comprobante', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('categoria', css_class='col-md-4'),
                Column('monto', css_class='col-md-3'),
                Column('moneda', css_class='col-md-2'),
                Column('tipo', css_class='col-md-3'),
            ),
            Row(
                Column('descripcion', css_class='col-md-6'),
                Column('fecha', css_class='col-md-3'),
            ),
            'comprobante',
            'notas',
            Submit('submit', 'Registrar Gasto', css_class='btn btn-success mt-2'),
        )


class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ['organismo', 'numero_expediente', 'estado', 'fecha_solicitud', 'fecha_aprobacion', 'plazo_dias', 'observaciones', 'documento']
        widgets = {
            'fecha_solicitud': forms.DateInput(attrs={'type': 'date'}),
            'fecha_aprobacion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('organismo', css_class='col-md-4'),
                Column('numero_expediente', css_class='col-md-4'),
                Column('estado', css_class='col-md-4'),
            ),
            Row(
                Column('fecha_solicitud', css_class='col-md-3'),
                Column('fecha_aprobacion', css_class='col-md-3'),
                Column('plazo_dias', css_class='col-md-3'),
            ),
            'observaciones',
            'documento',
            Submit('submit', 'Guardar Permiso', css_class='btn btn-primary mt-2'),
        )


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['tipo', 'nombre', 'archivo', 'notas']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('tipo', css_class='col-md-4'),
                Column('nombre', css_class='col-md-8'),
            ),
            'archivo',
            'notas',
            Submit('submit', 'Subir Documento', css_class='btn btn-secondary mt-2'),
        )


class NotaRapidaForm(forms.ModelForm):
    class Meta:
        model = EventoTimeline
        fields = ['descripcion']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Agregar nota...'})}
        labels = {'descripcion': ''}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'descripcion',
            Submit('submit', 'Agregar nota', css_class='btn btn-outline-secondary btn-sm mt-1'),
        )


class ImportadorForm(forms.ModelForm):
    class Meta:
        model = Importador
        fields = ['nombre', 'ruc', 'telefono', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'nombre',
            Row(Column('ruc', css_class='col-md-4'), Column('telefono', css_class='col-md-4'), Column('email', css_class='col-md-4')),
            Submit('submit', 'Guardar', css_class='btn btn-primary mt-2'),
        )
