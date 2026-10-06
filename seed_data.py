"""
Datos de demo para el sistema M2R.
Ejecutar: python manage.py shell < seed_data.py
"""
import os, django, datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'm2r_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from contenedores.models import Contenedor, Importador, Gasto, Permiso, EventoTimeline
from flota.models import Camion, Chofer

# Superusuario
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@m2rgroup.com.py', 'admin123')
    print('Superusuario admin/admin123 creado')

admin = User.objects.get(username='admin')
hoy = datetime.date.today()

# Choferes
ch1 = Chofer.objects.get_or_create(nombre='Carlos Rodríguez', defaults={'cedula': '3.456.789', 'telefono': '0981-445566'})[0]
ch2 = Chofer.objects.get_or_create(nombre='Miguel Ávalos', defaults={'cedula': '4.123.456', 'telefono': '0982-334455'})[0]

# Camiones
cam1 = Camion.objects.get_or_create(matricula='ABCD 123', defaults={'marca': 'Mercedes-Benz', 'modelo': 'Actros', 'anio': 2019, 'estado': 'en_ruta', 'chofer_asignado': ch1})[0]
cam2 = Camion.objects.get_or_create(matricula='EFGH 456', defaults={'marca': 'Scania', 'modelo': 'R450', 'anio': 2021, 'estado': 'disponible', 'chofer_asignado': ch2})[0]
cam3 = Camion.objects.get_or_create(matricula='IJKL 789', defaults={'marca': 'Volvo', 'modelo': 'FH16', 'anio': 2020, 'estado': 'disponible'})[0]

# Importadores
imp1 = Importador.objects.get_or_create(nombre='Distribuidora Central S.A.', defaults={'ruc': '80005678-1', 'telefono': '021-448899', 'email': 'ops@distcentral.com.py'})[0]
imp2 = Importador.objects.get_or_create(nombre='Agro Import Paraguay', defaults={'ruc': '80009876-5', 'telefono': '021-567234'})[0]
imp3 = Importador.objects.get_or_create(nombre='Tech Solutions PY', defaults={'ruc': '80001234-7', 'email': 'import@techspy.com'})[0]

# Contenedores de prueba
contenedores_data = [
    {
        'numero': 'MSCU7654321',
        'tipo': '40HC',
        'estado': 'en_transito',
        'bl_numero': 'MSCU123456789',
        'naviera': 'MSC',
        'navio': 'MSC OSCAR',
        'puerto_origen': 'Buenaventura, Colombia',
        'eta': hoy + datetime.timedelta(days=12),
        'ultimo_dia_libre': hoy + datetime.timedelta(days=18),
        'importador': imp1,
        'descripcion_carga': 'Electrodomésticos mixtos',
        'ncm': '8516.60',
        'valor_cif_usd': 85000,
    },
    {
        'numero': 'CMAU1234567',
        'tipo': '40HC',
        'estado': 'aduana_py',
        'bl_numero': 'CMA789012345',
        'naviera': 'CMA CGM',
        'navio': 'CMA CGM MARCO POLO',
        'puerto_origen': 'Santos, Brasil',
        'eta': hoy - datetime.timedelta(days=3),
        'fecha_llegada': hoy - datetime.timedelta(days=3),
        'ultimo_dia_libre': hoy + datetime.timedelta(days=2),
        'importador': imp2,
        'camion': cam1,
        'descripcion_carga': 'Insumos agrícolas — fertilizantes',
        'ncm': '3105.20',
        'valor_cif_usd': 42000,
    },
    {
        'numero': 'HLXU9876543',
        'tipo': '40HC',
        'estado': 'terminal',
        'bl_numero': 'HLX556677889',
        'naviera': 'Hapag-Lloyd',
        'navio': 'TIHAMA',
        'puerto_origen': 'Montevideo, Uruguay',
        'eta': hoy - datetime.timedelta(days=7),
        'fecha_llegada': hoy - datetime.timedelta(days=7),
        'ultimo_dia_libre': hoy - datetime.timedelta(days=2),  # demurrage vencido
        'importador': imp3,
        'descripcion_carga': 'Equipos de informática y servidores',
        'ncm': '8471.30',
        'valor_cif_usd': 120000,
    },
    {
        'numero': 'SUDU5555555',
        'tipo': '20DV',
        'estado': 'liberado',
        'bl_numero': 'SUD334455667',
        'naviera': 'Sudan Shipping',
        'puerto_origen': 'Buenos Aires, Argentina',
        'eta': hoy - datetime.timedelta(days=14),
        'fecha_llegada': hoy - datetime.timedelta(days=14),
        'fecha_liberacion': hoy - datetime.timedelta(days=1),
        'ultimo_dia_libre': hoy + datetime.timedelta(days=5),
        'importador': imp1,
        'camion': cam2,
        'descripcion_carga': 'Textiles e indumentaria',
        'valor_cif_usd': 18000,
    },
]

for data in contenedores_data:
    num = data['numero']
    if not Contenedor.objects.filter(numero=num).exists():
        c = Contenedor.objects.create(creado_por=admin, **data)
        EventoTimeline.objects.create(
            contenedor=c,
            tipo='estado',
            titulo='Carpeta creada (demo)',
            usuario=admin,
            automatico=True,
        )

# Gastos para CMAU1234567
c_cmau = Contenedor.objects.get(numero='CMAU1234567')
gastos = [
    {'categoria': 'flete', 'monto': 2800, 'moneda': 'USD', 'tipo': 'real'},
    {'categoria': 'thc', 'monto': 380, 'moneda': 'USD', 'tipo': 'real'},
    {'categoria': 'despachante', 'monto': 500, 'moneda': 'USD', 'tipo': 'presupuestado'},
    {'categoria': 'arancel', 'monto': 2940, 'moneda': 'USD', 'tipo': 'presupuestado'},
]
for g in gastos:
    if not c_cmau.gastos.filter(categoria=g['categoria'], tipo=g['tipo']).exists():
        Gasto.objects.create(contenedor=c_cmau, registrado_por=admin, **g)

# Gastos para HLXU9876543 (con demurrage)
c_hlxu = Contenedor.objects.get(numero='HLXU9876543')
gastos_hlxu = [
    {'categoria': 'flete', 'monto': 3500, 'moneda': 'USD', 'tipo': 'real'},
    {'categoria': 'thc', 'monto': 420, 'moneda': 'USD', 'tipo': 'real'},
    {'categoria': 'demurrage', 'monto': 340, 'moneda': 'USD', 'tipo': 'real'},
    {'categoria': 'permiso', 'monto': 150, 'moneda': 'USD', 'tipo': 'presupuestado'},
]
for g in gastos_hlxu:
    if not c_hlxu.gastos.filter(categoria=g['categoria'], tipo=g['tipo']).exists():
        Gasto.objects.create(contenedor=c_hlxu, registrado_por=admin, **g)

# Permisos para HLXU9876543
if not c_hlxu.permisos.filter(organismo='DINAVISA').exists():
    Permiso.objects.create(
        contenedor=c_hlxu,
        organismo='DINAVISA',
        estado='en_tramite',
        fecha_solicitud=hoy - datetime.timedelta(days=5),
        plazo_dias=10,
        observaciones='Tramitando certificado sanitario para equipos importados',
    )

# Permiso para CMAU1234567
if not c_cmau.permisos.filter(organismo='SENAVE').exists():
    Permiso.objects.create(
        contenedor=c_cmau,
        organismo='SENAVE',
        estado='aprobado',
        fecha_solicitud=hoy - datetime.timedelta(days=10),
        fecha_aprobacion=hoy - datetime.timedelta(days=2),
    )

print('Datos de demo cargados correctamente.')
print('Contenedores creados:', Contenedor.objects.count())
print('Login: admin / admin123')
