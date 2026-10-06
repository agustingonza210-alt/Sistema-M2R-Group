# Sistema M2R Group

Sistema de seguimiento de contenedores e importaciones para M2R Group — Paraguay.

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de configuración
cp .env.example .env
# Editar .env con tus claves API

# Crear base de datos
python manage.py migrate

# Cargar datos de demo (opcional)
python seed_data.py

# Iniciar servidor
python manage.py runserver
```

**Login demo:** `admin` / `admin123`

## Módulos

| Módulo | Descripción |
|---|---|
| `contenedores` | Carpeta por contenedor: estados, gastos, permisos, documentos, timeline |
| `flota` | Camiones y choferes |
| `tracking` | Clientes ShipsGo y Terminal49 |

## Flujo de estados

```
en_tránsito → aduana UY → aduana PY → terminal → liberado → entregado
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True` en desarrollo |
| `SHIPSGO_API_KEY` | API key de ShipsGo |
| `TERMINAL49_API_KEY` | API key de Terminal49 |
