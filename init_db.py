"""
init_db.py es un script de inicialización de la base de datos LogiTrack_Global.
 
Qué hace:
1. Se conecta a MongoDB reutilizando la misma configuración de .env
   que usa modelo/models.py .
2. Crea la colección 'viajes_monitoreo' con un validador $jsonSchema
   que obliga la estructura de tipos definida para el caso de estudio
   (vehículo, conductor, centro_contacto, telemetria_iot).
3. Crea la colección maestra 'conductores' (independiente de los
   viajes) con su propio validador $jsonSchema.
4. Crea los índices necesarios para las consultas más frecuentes:
   - codigo_ruta: único (no pueden existir dos viajes con el mismo código)
   - vehiculo.patente: único (no pueden existir dos vehículos con la misma patente)
   - conductor.rut_id: índice normal (se consulta mucho, pero un mismo
     conductor puede aparecer en más de un viaje/documento)
   - conductores.rut_id: único (identificador de cada conductor como
     entidad propia)
 
Cómo correrlo:
    python init_db.py este se corre 1 vez para prepara la base
    python main.py se corre siempre
 
"""
 
import sys
import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import (
    OperationFailure,
    ServerSelectionTimeoutError,
    ConfigurationError,
    CollectionInvalid,
)
from dotenv import load_dotenv
 
load_dotenv()
 
 
NOMBRE_COLECCION = "viajes_monitoreo"
NOMBRE_COLECCION_CONDUCTORES = "conductores"
 
 
VALIDADOR_ESQUEMA_CONDUCTORES = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["rut_id", "nombre"],
        "properties": {
            "rut_id": {"bsonType": "string", "description": "obligatorio, identificador único del conductor"},
            "nombre": {"bsonType": "string"},
            "primer_apellido": {"bsonType": "string"},
            "nacionalidad": {"bsonType": "string"},
            "tipo_licencia": {"bsonType": "string"},
            "fecha_vencimiento": {"bsonType": "string"},
            "anos_experiencia": {"bsonType": ["int", "double"], "minimum": 0},
            "observaciones": {"bsonType": "string"},
            "tutor": {"bsonType": ["string", "null"]},
            "supervisa_a": {"bsonType": "array"},
            "supervisor": {"bsonType": ["string", "null"]},
        },
    }
}
 
 
VALIDADOR_ESQUEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "codigo_ruta", "origen", "destino", "tiempo_estimado_dias",
            "estado_viaje", "vehiculo", "conductor", "telemetria_iot"
        ],
        "properties": {
            "codigo_ruta": {"bsonType": "string", "description": "obligatorio, string"},
            "origen": {"bsonType": "string"},
            "destino": {"bsonType": "string"},
            "tiempo_estimado_dias": {"bsonType": ["double", "int"], "minimum": 0},
            "estado_viaje": {
                "enum": ["PENDIENTE", "EN_TRANSITO", "FINALIZADO", "CANCELADO"]
            },
            "peso_mercancia_kg": {"bsonType": ["double", "int"], "minimum": 0},
            "tipo_combustible": {
                "enum": ["Diesel", "Gasolina", "GNC", "GLP", "Híbrido"]
            },
            "centro_contacto": {
                "bsonType": "object",
                "properties": {
                    "nombre": {"bsonType": "string"},
                    "telefono": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                },
            },
            "vehiculo": {
                "bsonType": "object",
                "required": ["patente"],
                "properties": {
                    "vin": {"bsonType": "string"},
                    "patente": {"bsonType": "string"},
                    "marca": {"bsonType": "string"},
                    "modelo": {"bsonType": "string"},
                    "ano_fabricacion": {"bsonType": "int"},
                    "capacidad_carga_max_Kg": {"bsonType": ["double", "int"], "minimum": 0},
                    "observaciones": {"bsonType": "string"},
                },
            },
            "conductor": {
                "bsonType": "object",
                "required": ["rut_id", "nombre"],
                "properties": {
                    "rut_id": {"bsonType": "string"},
                    "nombre": {"bsonType": "string"},
                    "primer_apellido": {"bsonType": "string"},
                    "nacionalidad": {"bsonType": "string"},
                    "tipo_licencia": {"bsonType": "string"},
                    "fecha_vencimiento": {"bsonType": "string"},
                    "capacitaciones": {"bsonType": "array"},
                    "observaciones": {"bsonType": "string"},
                    "tutor": {"bsonType": ["string", "null"]},
                    "supervisa_a": {"bsonType": "array"},
                    "supervisor": {"bsonType": ["string", "null"]},
                },
            },
            "telemetria_iot": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "properties": {
                        "timestamp": {"bsonType": "date"},
                        "km_recorridos": {"bsonType": ["double", "int"]},
                        "litros_consumidos": {"bsonType": ["double", "int"]},
                        "emision_co2_kg": {"bsonType": ["double", "int"]},
                        "velocidad_kmh": {"bsonType": ["double", "int"]},
                        "temperatura_motor_c": {"bsonType": ["double", "int"]},
                        "nivel_combustible_pct": {"bsonType": ["double", "int"]},
                        "alertas": {"bsonType": "array"},
                    },
                },
            },
        },
    }
}
 
 
def construir_uri(database_name):
    """Misma lógica que modelo/models.py: prioriza MONGO_URI si existe,
    si no arma la URI con usuario de mínimo privilegio."""
    uri_completa = os.getenv("MONGO_URI")
    if uri_completa:
        return uri_completa
 
    host = os.getenv("MONGO_HOST", "localhost")
    puerto = os.getenv("MONGO_PORT", "27017")
    usuario = os.getenv("MONGO_APP_USER", "")
    password = os.getenv("MONGO_APP_PASSWORD", "")
    auth_source = os.getenv("MONGO_AUTH_SOURCE", database_name)
 
    if usuario and password:
        return f"mongodb://{usuario}:{password}@{host}:{puerto}/?authSource={auth_source}"
 
    print("[AVISO] Sin credenciales en .env, conectando sin autenticación "
          "(solo válido para desarrollo local).")
    return f"mongodb://{host}:{puerto}/"
 
 
def main():
    database_name = os.getenv("MONGO_DB_NAME", "logitrack_db")
    uri = construir_uri(database_name)
    usar_tls = os.getenv("MONGO_TLS", "false").strip().lower() == "true"
 
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000, tls=usar_tls)
        client.server_info()
        db = client[database_name]
        print(f"Conectado a MongoDB (base de datos '{database_name}').")
 
    except OperationFailure:
        print("[ERROR] Usuario o contraseña incorrectos, o sin permisos "
              "sobre la base de datos.")
        sys.exit(1)
    except ServerSelectionTimeoutError:
        print("[ERROR] No se pudo contactar al servidor de MongoDB. "
              "¿Está corriendo el servicio?")
        sys.exit(1)
    except ConfigurationError as e:
        print(f"[ERROR] Configuración de conexión inválida: {e}")
        sys.exit(1)
 
    # --- Crear colección con validador, o aplicar validador si ya existe ---
    colecciones_existentes = db.list_collection_names()
 
    try:
        if NOMBRE_COLECCION not in colecciones_existentes:
            db.create_collection(NOMBRE_COLECCION, validator=VALIDADOR_ESQUEMA)
            print(f"Colección '{NOMBRE_COLECCION}' creada con validador de esquema.")
        else:
            db.command({
                "collMod": NOMBRE_COLECCION,
                "validator": VALIDADOR_ESQUEMA,
                "validationLevel": "moderate",  # valida inserts/updates nuevos,
                                                  # no rompe documentos viejos
            })
            print(f"Validador de esquema aplicado a la colección existente "
                  f"'{NOMBRE_COLECCION}'.")
    except CollectionInvalid as e:
        print(f"[ERROR] No se pudo crear la colección: {e}")
        sys.exit(1)
    except OperationFailure as e:
        print(f"[ERROR] No se pudo aplicar el validador (¿permisos insuficientes?): {e}")
        sys.exit(1)
 
    # --- Índices de viajes_monitoreo ---
    coleccion = db[NOMBRE_COLECCION]
    try:
        # codigo_ruta SÍ es único: es el identificador de cada documento/viaje.
        coleccion.create_index([("codigo_ruta", ASCENDING)], unique=True, name="idx_codigo_ruta_unico")
        coleccion.create_index([("vehiculo.patente", ASCENDING)], name="idx_patente")
        coleccion.create_index([("conductor.rut_id", ASCENDING)], name="idx_conductor_rut")
        print("Índices creados: codigo_ruta (único), vehiculo.patente, conductor.rut_id.")
    except OperationFailure as e:
        print(f"[ERROR] No se pudieron crear los índices: {e}")
        sys.exit(1)
 
    # --- Colección maestra "conductores" (independiente de los viajes) ---
    try:
        if NOMBRE_COLECCION_CONDUCTORES not in colecciones_existentes:
            db.create_collection(NOMBRE_COLECCION_CONDUCTORES, validator=VALIDADOR_ESQUEMA_CONDUCTORES)
            print(f"Colección '{NOMBRE_COLECCION_CONDUCTORES}' creada con validador de esquema.")
        else:
            db.command({
                "collMod": NOMBRE_COLECCION_CONDUCTORES,
                "validator": VALIDADOR_ESQUEMA_CONDUCTORES,
                "validationLevel": "moderate",
            })
            print(f"Validador de esquema aplicado a la colección existente "
                  f"'{NOMBRE_COLECCION_CONDUCTORES}'.")
    except CollectionInvalid as e:
        print(f"[ERROR] No se pudo crear la colección '{NOMBRE_COLECCION_CONDUCTORES}': {e}")
        sys.exit(1)
    except OperationFailure as e:
        print(f"[ERROR] No se pudo aplicar el validador a '{NOMBRE_COLECCION_CONDUCTORES}' "
              f"(¿permisos insuficientes?): {e}")
        sys.exit(1)
 
    coleccion_conductores = db[NOMBRE_COLECCION_CONDUCTORES]
    try:
        # rut_id es único acá: es el identificador de cada conductor
        # como entidad propia, independiente de los viajes que haga.
        coleccion_conductores.create_index([("rut_id", ASCENDING)], unique=True, name="idx_rut_id_unico")
        print("Índice creado: conductores.rut_id (único).")
    except OperationFailure as e:
        print(f"[ERROR] No se pudo crear el índice en '{NOMBRE_COLECCION_CONDUCTORES}': {e}")
        sys.exit(1)
 
    print("\nInicialización completa.")
    client.close()
 
 
if __name__ == "__main__":
    main()
 