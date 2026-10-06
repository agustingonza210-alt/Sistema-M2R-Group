from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from contenedores.models import Contenedor, EventoTimeline
from .shipsgo_client import get_container_info, parse_tracking_data
from .terminal49_client import parse_terminal_data
from .models import TrackingSnapshot
from django.utils import timezone


@login_required
def actualizar_tracking(request, pk):
    contenedor = get_object_or_404(Contenedor, pk=pk)

    raw = get_container_info(contenedor.numero)
    datos = parse_tracking_data(raw)

    exitoso = 'error' not in datos
    TrackingSnapshot.objects.create(
        contenedor_numero=contenedor.numero,
        fuente='shipsgo',
        datos_raw=raw,
        exitoso=exitoso,
    )

    if exitoso:
        if datos.get('naviera') and not contenedor.naviera:
            contenedor.naviera = datos['naviera']
        if datos.get('navio') and not contenedor.navio:
            contenedor.navio = datos['navio']
        if datos.get('eta'):
            from datetime import datetime
            try:
                contenedor.eta = datetime.fromisoformat(datos['eta']).date()
            except (ValueError, TypeError):
                pass
        contenedor.save()

        EventoTimeline.objects.create(
            contenedor=contenedor,
            tipo='tracking',
            titulo=f'Tracking actualizado via ShipsGo',
            descripcion=datos.get('ultimo_evento', ''),
            usuario=request.user,
            automatico=False,
        )
        messages.success(request, f'Tracking de {contenedor.numero} actualizado.')
    else:
        messages.error(request, f'Error al consultar ShipsGo: {datos.get("error")}')

    return redirect('contenedores:detalle', pk=pk)


@login_required
def tracking_json(request, pk):
    """Endpoint JSON para polling desde el frontend."""
    contenedor = get_object_or_404(Contenedor, pk=pk)
    snapshot = TrackingSnapshot.objects.filter(
        contenedor_numero=contenedor.numero, exitoso=True
    ).first()

    if not snapshot:
        return JsonResponse({'estado': 'sin_datos'})

    return JsonResponse({
        'estado': contenedor.get_estado_display(),
        'semaforo': contenedor.semaforo_demurrage,
        'dias_libres': contenedor.dias_libres_restantes,
        'dias_demurrage': contenedor.dias_demurrage_acumulados,
        'ultima_actualizacion': snapshot.consultado_en.isoformat(),
        'datos': snapshot.datos_raw,
    })
