"""
Cliente para la API de Terminal49.
Soporta específicamente el Puerto de Asunción y terminales de la Hidrovía.
Documentación: https://terminal49.com/docs/api

Puertos cubiertos:
  - Puerto de Asunción (PYASU)
  - Caacupe-Mi (PYCAC)
  - Puerto Fenix (PYPFE)
  - Puerto San José (PYPSJ)
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

TERMINAL49_BASE = 'https://api.terminal49.com/v2'


def _headers():
    return {
        'Authorization': f'Token {settings.TERMINAL49_API_KEY}',
        'Content-Type': 'application/json',
    }


def track_container(container_number: str, bl_number: str = '') -> dict:
    """Inicia el tracking de un contenedor en Terminal49."""
    if not settings.TERMINAL49_API_KEY:
        return {'error': 'TERMINAL49_API_KEY no configurado'}
    try:
        payload = {
            'data': {
                'type': 'tracking_request',
                'attributes': {
                    'request_number': container_number,
                    'request_type': 'container',
                }
            }
        }
        if bl_number:
            payload['data']['attributes']['ref_numbers'] = [bl_number]

        resp = requests.post(
            f'{TERMINAL49_BASE}/tracking_requests',
            json=payload, headers=_headers(), timeout=15
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error('Terminal49 track_container error: %s', e)
        return {'error': str(e)}


def get_shipment(shipment_id: str) -> dict:
    """Obtiene datos completos de un shipment por ID de Terminal49."""
    if not settings.TERMINAL49_API_KEY:
        return {'error': 'TERMINAL49_API_KEY no configurado'}
    try:
        resp = requests.get(
            f'{TERMINAL49_BASE}/shipments/{shipment_id}',
            headers=_headers(), timeout=15
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error('Terminal49 get_shipment error: %s', e)
        return {'error': str(e)}


def parse_terminal_data(raw: dict) -> dict:
    """Normaliza la respuesta de Terminal49 a nuestro formato interno."""
    if 'error' in raw:
        return raw

    attrs = raw.get('data', {}).get('attributes', {})
    pod_info = attrs.get('pod', {}) or {}

    return {
        'numero': attrs.get('container_number', ''),
        'naviera': attrs.get('shipping_line', {}).get('name', '') if attrs.get('shipping_line') else '',
        'navio': attrs.get('vessel', {}).get('name', '') if attrs.get('vessel') else '',
        'eta': pod_info.get('estimated_arrival_at', ''),
        'disponible_retiro': attrs.get('available_for_pickup', False),
        'ultimo_dia_libre': attrs.get('pickup_lfd', ''),
        'holds_pendientes': attrs.get('holds', []),
        'en_patio_terminal': attrs.get('pod_arrived_at') is not None,
        'ultimo_evento': attrs.get('raw_events', [{}])[0].get('description', '') if attrs.get('raw_events') else '',
        'fuente': 'terminal49',
    }
