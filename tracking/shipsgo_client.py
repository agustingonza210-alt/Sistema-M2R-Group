"""
Cliente para la API de ShipsGo.
Documentación: https://shipsgo.com/api
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SHIPSGO_API_BASE = 'https://shipsgo.com/api/v1.2'


def _headers():
    return {
        'Content-Type': 'application/json',
        'ShipsgoApiKey': settings.SHIPSGO_API_KEY,
    }


def add_container(container_number: str, bl_number: str = '') -> dict:
    """Agrega un contenedor a ShipsGo para tracking."""
    if not settings.SHIPSGO_API_KEY:
        return {'error': 'SHIPSGO_API_KEY no configurado'}
    try:
        payload = {
            'containerNumber': container_number,
            'blNumber': bl_number,
        }
        resp = requests.post(
            f'{SHIPSGO_API_BASE}/ContainerService/AddContainerInfo',
            json=payload, headers=_headers(), timeout=15
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error('ShipsGo add_container error: %s', e)
        return {'error': str(e)}


def get_container_info(container_number: str) -> dict:
    """Obtiene el estado actual de un contenedor."""
    if not settings.SHIPSGO_API_KEY:
        return {'error': 'SHIPSGO_API_KEY no configurado'}
    try:
        params = {'containerNumber': container_number}
        resp = requests.get(
            f'{SHIPSGO_API_BASE}/ContainerService/GetContainerInfo',
            params=params, headers=_headers(), timeout=15
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error('ShipsGo get_container_info error: %s', e)
        return {'error': str(e)}


def parse_tracking_data(raw: dict) -> dict:
    """Normaliza la respuesta de ShipsGo a nuestro formato interno."""
    if 'error' in raw:
        return raw
    return {
        'numero': raw.get('containerNumber', ''),
        'naviera': raw.get('shippingLine', ''),
        'navio': raw.get('vesselName', ''),
        'puerto_origen': raw.get('pol', ''),
        'puerto_destino': raw.get('pod', ''),
        'eta': raw.get('eta', ''),
        'estado_naviero': raw.get('status', ''),
        'ultima_ubicacion': raw.get('lastEvent', {}).get('location', ''),
        'ultimo_evento': raw.get('lastEvent', {}).get('description', ''),
        'ultimo_evento_fecha': raw.get('lastEvent', {}).get('date', ''),
        'fuente': 'shipsgo',
    }
