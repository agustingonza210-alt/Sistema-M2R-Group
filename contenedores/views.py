from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Contenedor, Gasto, Permiso, Documento, EventoTimeline, Importador
from .forms import (
    ContenedorForm, GastoForm, PermisoForm,
    DocumentoForm, NotaRapidaForm, ImportadorForm
)


@login_required
def dashboard(request):
    hoy = timezone.now().date()

    contenedores_activos = Contenedor.objects.exclude(estado__in=['entregado', 'cancelado'])

    # Métricas del dashboard
    en_transito = contenedores_activos.filter(estado='en_transito').count()
    en_aduana = contenedores_activos.filter(estado__in=['aduana_uy', 'aduana_py']).count()
    en_terminal = contenedores_activos.filter(estado='terminal').count()
    liberados = contenedores_activos.filter(estado='liberado').count()

    # Alertas de demurrage
    alertas_rojas = [c for c in contenedores_activos if c.semaforo_demurrage == 'rojo']
    alertas_amarillas = [c for c in contenedores_activos if c.semaforo_demurrage == 'amarillo']

    # Contenedores con ETA próxima (7 días)
    proximas_llegadas = contenedores_activos.filter(
        eta__isnull=False,
        eta__range=[hoy, hoy + timezone.timedelta(days=7)]
    ).order_by('eta')

    # Todos los activos ordenados por semáforo de riesgo
    todos_activos = list(contenedores_activos.select_related('importador', 'camion').order_by('-creado_en'))

    context = {
        'en_transito': en_transito,
        'en_aduana': en_aduana,
        'en_terminal': en_terminal,
        'liberados': liberados,
        'total_activos': contenedores_activos.count(),
        'alertas_rojas': alertas_rojas,
        'alertas_amarillas': alertas_amarillas,
        'proximas_llegadas': proximas_llegadas,
        'contenedores': todos_activos,
        'titulo': 'Dashboard',
    }
    return render(request, 'contenedores/dashboard.html', context)


@login_required
def lista_contenedores(request):
    qs = Contenedor.objects.select_related('importador', 'camion', 'responsable')

    # Filtros
    estado = request.GET.get('estado', '')
    busqueda = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if busqueda:
        qs = qs.filter(
            Q(numero__icontains=busqueda) |
            Q(bl_numero__icontains=busqueda) |
            Q(navio__icontains=busqueda) |
            Q(importador__nombre__icontains=busqueda)
        )

    context = {
        'contenedores': qs,
        'estado_seleccionado': estado,
        'busqueda': busqueda,
        'estados': Contenedor.ESTADO_CHOICES,
        'titulo': 'Contenedores',
    }
    return render(request, 'contenedores/lista.html', context)


@login_required
def detalle_contenedor(request, pk):
    contenedor = get_object_or_404(
        Contenedor.objects.select_related('importador', 'camion', 'responsable'),
        pk=pk
    )
    gastos = contenedor.gastos.all()
    permisos = contenedor.permisos.all()
    documentos = contenedor.documentos.all()
    eventos = contenedor.eventos.all()[:20]

    nota_form = NotaRapidaForm()

    if request.method == 'POST' and 'nota_rapida' in request.POST:
        nota_form = NotaRapidaForm(request.POST)
        if nota_form.is_valid():
            EventoTimeline.objects.create(
                contenedor=contenedor,
                tipo='nota',
                titulo='Nota',
                descripcion=nota_form.cleaned_data['descripcion'],
                usuario=request.user,
            )
            messages.success(request, 'Nota agregada.')
            return redirect('contenedores:detalle', pk=pk)

    # Resumen gastos
    gastos_usd_real = sum(g.monto for g in gastos if g.moneda == 'USD' and g.tipo == 'real')
    gastos_usd_presup = sum(g.monto for g in gastos if g.moneda == 'USD' and g.tipo == 'presupuestado')

    # Permisos bloqueantes
    permisos_bloqueantes = [p for p in permisos if p.bloquea_despacho]

    context = {
        'contenedor': contenedor,
        'gastos': gastos,
        'permisos': permisos,
        'documentos': documentos,
        'eventos': eventos,
        'nota_form': nota_form,
        'gastos_usd_real': gastos_usd_real,
        'gastos_usd_presup': gastos_usd_presup,
        'permisos_bloqueantes': permisos_bloqueantes,
        'titulo': f'Carpeta {contenedor.numero}',
    }
    return render(request, 'contenedores/detalle.html', context)


@login_required
def nuevo_contenedor(request):
    if request.method == 'POST':
        form = ContenedorForm(request.POST)
        if form.is_valid():
            contenedor = form.save(commit=False)
            contenedor.creado_por = request.user
            contenedor.save()
            EventoTimeline.objects.create(
                contenedor=contenedor,
                tipo='estado',
                titulo='Carpeta creada',
                descripcion=f'Carpeta creada por {request.user.get_full_name() or request.user.username}',
                usuario=request.user,
            )
            messages.success(request, f'Contenedor {contenedor.numero} creado.')
            return redirect('contenedores:detalle', pk=contenedor.pk)
    else:
        form = ContenedorForm()

    return render(request, 'contenedores/form.html', {'form': form, 'titulo': 'Nuevo Contenedor', 'accion': 'Crear'})


@login_required
def editar_contenedor(request, pk):
    contenedor = get_object_or_404(Contenedor, pk=pk)
    estado_anterior = contenedor.estado

    if request.method == 'POST':
        form = ContenedorForm(request.POST, instance=contenedor)
        if form.is_valid():
            contenedor = form.save()
            if contenedor.estado != estado_anterior:
                EventoTimeline.objects.create(
                    contenedor=contenedor,
                    tipo='estado',
                    titulo=f'Estado cambiado: {contenedor.get_estado_display()}',
                    descripcion=f'Cambio de {dict(Contenedor.ESTADO_CHOICES).get(estado_anterior)} → {contenedor.get_estado_display()}',
                    usuario=request.user,
                )
            messages.success(request, 'Contenedor actualizado.')
            return redirect('contenedores:detalle', pk=contenedor.pk)
    else:
        form = ContenedorForm(instance=contenedor)

    return render(request, 'contenedores/form.html', {
        'form': form, 'contenedor': contenedor,
        'titulo': f'Editar {contenedor.numero}', 'accion': 'Guardar',
    })


@login_required
def agregar_gasto(request, pk):
    contenedor = get_object_or_404(Contenedor, pk=pk)
    if request.method == 'POST':
        form = GastoForm(request.POST, request.FILES)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.contenedor = contenedor
            gasto.registrado_por = request.user
            gasto.save()
            EventoTimeline.objects.create(
                contenedor=contenedor,
                tipo='gasto',
                titulo=f'Gasto: {gasto.get_categoria_display()}',
                descripcion=f'{gasto.moneda} {gasto.monto} ({gasto.get_tipo_display()})',
                usuario=request.user,
            )
            messages.success(request, 'Gasto registrado.')
            return redirect('contenedores:detalle', pk=pk)
    else:
        form = GastoForm()

    return render(request, 'contenedores/gasto_form.html', {
        'form': form, 'contenedor': contenedor, 'titulo': 'Registrar Gasto'
    })


@login_required
def agregar_permiso(request, pk):
    contenedor = get_object_or_404(Contenedor, pk=pk)
    if request.method == 'POST':
        form = PermisoForm(request.POST, request.FILES)
        if form.is_valid():
            permiso = form.save(commit=False)
            permiso.contenedor = contenedor
            permiso.save()
            EventoTimeline.objects.create(
                contenedor=contenedor,
                tipo='permiso',
                titulo=f'Permiso {permiso.organismo}: {permiso.get_estado_display()}',
                descripcion=permiso.observaciones,
                usuario=request.user,
            )
            messages.success(request, 'Permiso registrado.')
            return redirect('contenedores:detalle', pk=pk)
    else:
        form = PermisoForm()

    return render(request, 'contenedores/permiso_form.html', {
        'form': form, 'contenedor': contenedor, 'titulo': 'Registrar Permiso'
    })


@login_required
def editar_permiso(request, pk, permiso_pk):
    contenedor = get_object_or_404(Contenedor, pk=pk)
    permiso = get_object_or_404(Permiso, pk=permiso_pk, contenedor=contenedor)
    if request.method == 'POST':
        form = PermisoForm(request.POST, request.FILES, instance=permiso)
        if form.is_valid():
            permiso = form.save()
            EventoTimeline.objects.create(
                contenedor=contenedor,
                tipo='permiso',
                titulo=f'Permiso {permiso.organismo} actualizado: {permiso.get_estado_display()}',
                usuario=request.user,
            )
            messages.success(request, 'Permiso actualizado.')
            return redirect('contenedores:detalle', pk=pk)
    else:
        form = PermisoForm(instance=permiso)

    return render(request, 'contenedores/permiso_form.html', {
        'form': form, 'contenedor': contenedor, 'permiso': permiso, 'titulo': 'Editar Permiso'
    })


@login_required
def subir_documento(request, pk):
    contenedor = get_object_or_404(Contenedor, pk=pk)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.contenedor = contenedor
            doc.subido_por = request.user
            doc.save()
            EventoTimeline.objects.create(
                contenedor=contenedor,
                tipo='documento',
                titulo=f'Documento subido: {doc.get_tipo_display()}',
                descripcion=doc.nombre,
                usuario=request.user,
            )
            messages.success(request, 'Documento subido.')
            return redirect('contenedores:detalle', pk=pk)
    else:
        form = DocumentoForm()

    return render(request, 'contenedores/documento_form.html', {
        'form': form, 'contenedor': contenedor, 'titulo': 'Subir Documento'
    })


@login_required
def lista_importadores(request):
    importadores = Importador.objects.filter(activo=True)
    return render(request, 'contenedores/importadores.html', {
        'importadores': importadores, 'titulo': 'Importadores'
    })


@login_required
def nuevo_importador(request):
    if request.method == 'POST':
        form = ImportadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Importador creado.')
            return redirect('contenedores:importadores')
    else:
        form = ImportadorForm()
    return render(request, 'contenedores/importador_form.html', {'form': form, 'titulo': 'Nuevo Importador'})
