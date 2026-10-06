from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Camion, Chofer


class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = ['matricula', 'marca', 'modelo', 'anio', 'estado', 'chofer_asignado', 'notas']
        widgets = {'notas': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('matricula', css_class='col-md-3'),
                Column('marca', css_class='col-md-3'),
                Column('modelo', css_class='col-md-3'),
                Column('anio', css_class='col-md-3'),
            ),
            Row(
                Column('estado', css_class='col-md-4'),
                Column('chofer_asignado', css_class='col-md-8'),
            ),
            'notas',
            Submit('submit', 'Guardar', css_class='btn btn-primary mt-2'),
        )


@login_required
def lista_camiones(request):
    camiones = Camion.objects.filter(activo=True).select_related('chofer_asignado')
    return render(request, 'flota/lista.html', {'camiones': camiones, 'titulo': 'Flota'})


@login_required
def nuevo_camion(request):
    if request.method == 'POST':
        form = CamionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Camión registrado.')
            return redirect('flota:lista')
    else:
        form = CamionForm()
    return render(request, 'flota/form.html', {'form': form, 'titulo': 'Nuevo Camión'})


@login_required
def detalle_camion(request, pk):
    camion = get_object_or_404(Camion, pk=pk)
    contenedores = camion.contenedores.exclude(estado__in=['entregado', 'cancelado'])
    return render(request, 'flota/detalle.html', {
        'camion': camion, 'contenedores': contenedores, 'titulo': f'Camión {camion.matricula}'
    })


@login_required
def lista_choferes(request):
    choferes = Chofer.objects.filter(activo=True)
    return render(request, 'flota/choferes.html', {'choferes': choferes, 'titulo': 'Choferes'})
