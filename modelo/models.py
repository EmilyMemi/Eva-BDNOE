# Este es el Modelo del proyecto (la M de MVC).
# Básicamente todo lo que tiene que ver con MongoDB pasa por acá:
# guardar viajes, actualizar la telemetría de los sensores y sacar
# los reportes de CO2. El controller.py es el que llama a estas
# funciones, la vista nunca debería tocar este archivo directamente.
 
from pymongo import MongoClient
from datetime import datetime
import sys
 
 
class LogiTrackModel:
    # Estos son los combustibles que el controller tiene mapeados
    # con su factor de emisión, si llega uno que no está en esta
    # lista mejor lo rechazamos antes de guardar cualquier cosa.
    COMBUSTIBLES_VALIDOS = ["Diesel", "Gasolina", "GNC", "GLP", "Híbrido"]
 
    def __init__(self, uri="mongodb://localhost:27017/", database_name="logitrack_db"):
        # Apenas se crea el modelo, intento conectarme a Mongo.
        # Si el servicio no está prendido, mejor avisar altiro con un
        # mensaje entendible en vez de que reviente con un error feo.
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            self.client.server_info()  # esto "obliga" a probar la conexión ya
 
            self.db = self.client[database_name]
            self.coleccion = self.db["viajes_monitoreo"]
 
            print("Conectado a MongoDB sin problemas.")
 
        except Exception as e:
            print(f"\nERROR No se pudo conectar a MongoDB: {e}")
            print("Revisa que el servicio de MongoDB esté corriendo.")
            sys.exit(1)
 
    
    # Crear un viaje nuevo
    # ---------------------------------------------------------
    def crear_viaje(self, datos_viaje):
        
        if not datos_viaje or not isinstance(datos_viaje, dict):
            return False, "No se pudo crear el viaje: los datos ingresados no son válidos."
 
        try:
            codigo_ruta = str(datos_viaje.get("codigo_ruta", "")).strip()
            origen = str(datos_viaje.get("origen", "")).strip()
            destino = str(datos_viaje.get("destino", "")).strip()
            tipo_combustible = datos_viaje.get("tipo_combustible", "Diesel")
            peso_mercancia_kg = datos_viaje.get("peso_mercancia_kg", 0)
            volumen_m3 = datos_viaje.get("volumen_m3", 0)
            tiempo_estimado_dias = datos_viaje.get("tiempo_estimado_dias", 0)
 
            if not codigo_ruta:
                return False, "El código de ruta no puede estar vacío."
 
            if self.existe_ruta(codigo_ruta):
                return False, f"Ya existe un viaje con el código '{codigo_ruta}'."
 
            # antes esto no se revisaba, un viaje se podía crear sin
            # origen ni destino y quedaba guardado con strings vacíos
            if not origen or not destino:
                return False, "Debes ingresar la ciudad de origen y de destino."
 
            if tipo_combustible not in self.COMBUSTIBLES_VALIDOS:
                return False, (
                    f"Ese combustible no lo manejamos. Usa uno de estos: "
                    f"{', '.join(self.COMBUSTIBLES_VALIDOS)}."
                )
            peso_mercancia_kg = float(peso_mercancia_kg)
            volumen_m3 = float(volumen_m3)
            tiempo_estimado_dias = float(tiempo_estimado_dias)
 
            if peso_mercancia_kg < 0 or volumen_m3 < 0:
                return False, "El peso y el volumen no pueden ser números negativos."
 
            if tiempo_estimado_dias <= 0:
                return False, "El tiempo estimado del viaje debe ser mayor a 0."
 
            documento = {
                "codigo_ruta": codigo_ruta,
                "origen": origen,
                "destino": destino,
                "tiempo_estimado_dias": tiempo_estimado_dias,
                "estado_viaje": "EN_TRANSITO",
 
                "peso_mercancia_kg": peso_mercancia_kg,
                "volumen_m3": volumen_m3,
                "tipo_combustible": tipo_combustible,
 
                "vehiculo": {
                    # lo dejo en mayúsculas para que "jgkda128" y
                    # "JGKDA128" no se guarden como si fueran dos
                    # vehículos distintos
                    "patente": str(datos_viaje.get("patente_vehiculo", "")).strip().upper(),
                },
                "conductor": {
                    "rut_id": str(datos_viaje.get("rut_conductor", "")).strip(),
                    "nombre": str(datos_viaje.get("nombre_conductor", "")).strip(),
                },
 
                "telemetria_iot": []
            }
 
            self.coleccion.insert_one(documento)
            return True, f"Viaje '{codigo_ruta}' creado con éxito."
 
        except (ValueError, TypeError):
            # esto salta si peso/volumen/tiempo no se pudieron convertir a número
            return False, "El peso, el volumen y el tiempo estimado deben ser números válidos."
        except Exception as e:
            # cualquier otro error inesperado (ej. se cayó la conexión
            # a mitad de camino) lo atrapamos acá para no reventar
            print(f"ERROR interno en crear_viaje {e}")
            return False, "Ocurrió un error inesperado al crear el viaje."
 
 
    
    # Consultas (leer datos)
    def existe_ruta(self, codigo_ruta):
        if not codigo_ruta:
            return False
        try:
            return self.coleccion.count_documents({"codigo_ruta": codigo_ruta}) > 0
        except Exception as e:
            print(f"ERROR interno en existe_ruta {e}")
            return False
 
    def obtener_viaje(self, codigo_ruta):
        if not codigo_ruta:
            return None
        try:
            return self.coleccion.find_one({"codigo_ruta": codigo_ruta})
        except Exception as e:
            print(f"ERROR interno en obtener_viaje {e}")
            return None
 
    def listar_viajes(self):
        try:
            cursor = self.coleccion.find(
                {},
                {"codigo_ruta": 1, "origen": 1, "destino": 1, "estado_viaje": 1, "_id": 0}
            )
            return list(cursor)
        except Exception as e:
            print(f"ERROR interno en listar_viajes {e}")
            return []
 
    def obtener_combustible_viaje(self, codigo_ruta):
        # El controller necesita esto antes de calcular las emisiones,
        # así que si algo falla, mejor devolver "Diesel" por defecto
        # que dejar caer todo el programa.
        viaje = self.obtener_viaje(codigo_ruta)
        if viaje:
            return viaje.get("tipo_combustible", "Diesel")
        return "Diesel"
 
    def obtener_alertas_activas(self):
        alertas_encontradas = []
        try:
            cursor = self.coleccion.find(
                {"telemetria_iot.alerta_sistema": {"$ne": None}}
            )
            for viaje in cursor:
                for lectura in viaje.get("telemetria_iot", []):
                    if lectura.get("alerta_sistema"):
                        alertas_encontradas.append({
                            "codigo_ruta": viaje.get("codigo_ruta"),
                            "alerta": lectura.get("alerta_sistema"),
                            "timestamp": lectura.get("timestamp")
                        })
        except Exception as e:
            print(f"ERROR interno en obtener_alertas_activas {e}")
 
        return alertas_encontradas
 
    
    # Actualizar telemetría (cada vez que llega una lectura del sensor)
    def actualizar_telemetria(self, codigo_ruta, datos_sensores):
        # Mismo cuidado que en crear_viaje: si la vista canceló el
        # ingreso, datos_sensores puede llegar como None.
        if not datos_sensores or not isinstance(datos_sensores, dict):
            return False, "No se pudo actualizar: los datos del sensor no son válidos."
 
        if not codigo_ruta:
            return False, "Debes indicar un código de ruta."
 
        if not self.existe_ruta(codigo_ruta):
            return False, f"No existe ningún viaje con el código '{codigo_ruta}'."
 
        try:
            km = float(datos_sensores.get("kilometros_recorridos_tramo", 0))
            litros = float(datos_sensores.get("litros_consumidos", 0))
 
            if km < 0 or litros < 0:
                return False, "Los kilómetros y los litros no pueden ser negativos."
 
            datos_sensores["timestamp"] = datetime.now()
 
            self.coleccion.update_one(
                {"codigo_ruta": codigo_ruta},
                {"$push": {"telemetria_iot": datos_sensores}}
            )
 
            return True, f"Telemetría guardada para la ruta '{codigo_ruta}'."
 
        except (ValueError, TypeError):
            return False, "Los kilómetros y los litros deben ser números válidos."
        except Exception as e:
            print(f"ERROR interno en actualizar_telemetria {e}")
            return False, "Ocurrió un error inesperado al guardar la telemetría."
 
    # Eliminar un viaje (por si se ingresó algo mal)
    def eliminar_viaje(self, codigo_ruta):
        if not codigo_ruta:
            return False, "Debes indicar un código de ruta."
 
        if not self.existe_ruta(codigo_ruta):
            return False, f"No existe ningún viaje con el código '{codigo_ruta}'."
 
        try:
            self.coleccion.delete_one({"codigo_ruta": codigo_ruta})
            return True, f"Viaje '{codigo_ruta}' eliminado."
        except Exception as e:
            print(f"ERROR interno en eliminar_viaje {e}")
            return False, "Ocurrió un error inesperado al eliminar el viaje."
 
    # Reporte de huella de carbono
    def obtener_reporte_carbono(self):
        try:
            pipeline = [
                {"$unwind": "$telemetria_iot"},
                {
                    "$group": {
                        "_id": "$vehiculo.patente",
                        "total_km": {"$sum": "$telemetria_iot.kilometros_recorridos_tramo"},
                        "total_litros": {"$sum": "$telemetria_iot.litros_consumidos"},
                        "total_co2_kg": {"$sum": "$telemetria_iot.emision_co2_kg"}
                    }
                },
                {"$sort": {"total_co2_kg": -1}}
            ]
 
            resultados = list(self.coleccion.aggregate(pipeline))
 
            for fila in resultados:
                fila["total_co2_toneladas"] = round(fila.get("total_co2_kg", 0) / 1000, 4)
 
            return resultados
 
        except Exception as e:
            print(f"ERROR interno en obtener_reporte_carbono {e}")
            return []
 
    # Cerrar la conexión al salir del programa
    def cerrar_conexion(self):
        try:
            self.client.close()
            print("Conexión a MongoDB cerrada.")
        except Exception as e:
            print(f"ERROR interno al cerrar conexión] {e}")
 