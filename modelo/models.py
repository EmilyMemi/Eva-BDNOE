
# actualizar la telemetría de los sensores, gestionar la jerarquía de
# conductores y sacar los reportes de CO2. El controller.py es el que
# llama a estas funciones, la vista nunca debería tocar este archivo
# directamente.
 
from pymongo import MongoClient
from datetime import datetime
import sys
 
 
class LogiTrackModel:
    # Combustibles que el sistema reconoce, con sus factores de
    # consumo y emisión (usados en actualizar_telemetria).
    COMBUSTIBLES_VALIDOS = ["Diesel", "Gasolina", "GNC", "GLP", "Híbrido"]
 
    # Litros que gasta el vehículo por cada km recorrido, según el
    # tipo de combustible (estimación para calcular consumo automático)
    FACTORES_CONSUMO = {
        "Diesel": 0.23,
        "Gasolina": 0.12,
        "GNC": 0.09,
        "GLP": 0.10,
        "Híbrido": 0.07
    }
 
    # kg de CO2 emitidos por cada litro consumido (norma ISO 14083 / MITECO)
    FACTORES_EMISION = {
        "Diesel": 2.68,
        "Gasolina": 2.35,
        "GNC": 2.72,
        "GLP": 1.66,
        "Híbrido": 1.45
    }
 
    # Tipos de licencia de conducir que aceptamos para el conductor
    LICENCIAS_VALIDAS = {"A1", "A2", "A3", "B", "C", "D", "E", "F"}
 
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
            print(f"\n[ERROR] No se pudo conectar a MongoDB: {e}")
            print("Revisa que el servicio de MongoDB esté corriendo.")
            sys.exit(1)
 
    # Crear un viaje nuevo
    def crear_viaje(self, datos_viaje):
        # OJO ACÁ: si la vista canceló el ingreso (por ejemplo porque
        # el usuario escribió una letra donde iba un número), nos
        # puede llegar None en vez de un diccionario. Si no reviso
        # esto primero, el programa se cae feo con un AttributeError.
        if not datos_viaje or not isinstance(datos_viaje, dict):
            return False, "No se pudo crear el viaje: los datos ingresados no son válidos."
 
        try:
            codigo_ruta = str(datos_viaje.get("codigo_ruta", "")).strip()
            origen = str(datos_viaje.get("origen", "")).strip()
            destino = str(datos_viaje.get("destino", "")).strip()
            tipo_combustible = datos_viaje.get("tipo_combustible", "Diesel")
            peso_mercancia_kg = datos_viaje.get("peso_mercancia_kg", 0)
            tiempo_estimado_dias = datos_viaje.get("tiempo_estimado_dias", 0)
 
            if not codigo_ruta:
                return False, "El código de ruta no puede estar vacío."
 
            if self.existe_ruta(codigo_ruta):
                return False, f"Ya existe un viaje con el código '{codigo_ruta}'."
 
            if not origen or not destino:
                return False, "Debes ingresar la ciudad de origen y de destino."
 
            if tipo_combustible not in self.COMBUSTIBLES_VALIDOS:
                return False, (
                    f"Ese combustible no lo manejamos. Usa uno de estos: "
                    f"{', '.join(self.COMBUSTIBLES_VALIDOS)}."
                )
 
           
            peso_mercancia_kg = float(peso_mercancia_kg)
            tiempo_estimado_dias = float(tiempo_estimado_dias)
 
            if peso_mercancia_kg < 0:
                return False, "El peso de la mercancía no puede ser negativo."
 
            if tiempo_estimado_dias <= 0:
                return False, "El tiempo estimado del viaje debe ser mayor a 0."
 
            # --- Centro de contacto de despacho ---
            centro_contacto = datos_viaje.get("centro_contacto", {})
            nombre_contacto = str(centro_contacto.get("nombre", "")).strip()
            telefono_contacto = str(centro_contacto.get("telefono", "")).strip()
            email_contacto = str(centro_contacto.get("email", "")).strip()
 
            # --- Datos del vehículo ---
            vehiculo = datos_viaje.get("vehiculo", {})
            vin = str(vehiculo.get("vin", "")).strip()
            patente = str(vehiculo.get("patente", "")).strip().upper()
            marca = str(vehiculo.get("marca", "")).strip()
            modelo_vehiculo = str(vehiculo.get("modelo", "")).strip()
            ano_fabricacion = vehiculo.get("ano_fabricacion", 0)
            capacidad_carga_max = vehiculo.get("capacidad_carga_max_Kg", 0)
            observaciones_vehiculo = str(vehiculo.get("observaciones", "")).strip()
 
            ano_fabricacion = int(ano_fabricacion)
            capacidad_carga_max = float(capacidad_carga_max)
 
            if not patente:
                return False, "La patente del vehículo es obligatoria."
 
            # --- Datos del conductor ---
            conductor = datos_viaje.get("conductor", {})
            rut_id = str(conductor.get("rut_id", "")).strip()
            nombre = str(conductor.get("nombre", "")).strip()
            primer_apellido = str(conductor.get("primer_apellido", "")).strip()
            nacionalidad = str(conductor.get("nacionalidad", "")).strip()
            tipo_licencia = str(conductor.get("tipo_licencia", "")).strip().upper()
            fecha_vencimiento_str = str(conductor.get("fecha_vencimiento", "")).strip()
            capacitaciones = conductor.get("capacitaciones", [])
            observaciones_conductor = str(conductor.get("observaciones", "")).strip()
 
            if not rut_id or not nombre:
                return False, "El RUT y el nombre del conductor son obligatorios."
 
            if tipo_licencia and tipo_licencia not in self.LICENCIAS_VALIDAS:
                return False, (
                    f"Tipo de licencia inválido. Usa una de estas: "
                    f"{', '.join(sorted(self.LICENCIAS_VALIDAS))}."
                )
 
            documento = {
                "codigo_ruta": codigo_ruta,
                "origen": origen,
                "destino": destino,
                "tiempo_estimado_dias": tiempo_estimado_dias,
                "estado_viaje": "PENDIENTE",
 
                "peso_mercancia_kg": peso_mercancia_kg,
                "tipo_combustible": tipo_combustible,
 
                "centro_contacto": {
                    "nombre": nombre_contacto,
                    "telefono": telefono_contacto,
                    "email": email_contacto
                },
 
                "vehiculo": {
                    "vin": vin,
                    "patente": patente,
                    "marca": marca,
                    "modelo": modelo_vehiculo,
                    "ano_fabricacion": ano_fabricacion,
                    "capacidad_carga_max_Kg": capacidad_carga_max,
                    "observaciones": observaciones_vehiculo
                },
 
                "conductor": {
                    "rut_id": rut_id,
                    "nombre": nombre,
                    "primer_apellido": primer_apellido,
                    "nacionalidad": nacionalidad,
                    "tipo_licencia": tipo_licencia,
                    "fecha_vencimiento": fecha_vencimiento_str,
                    "capacitaciones": capacitaciones,
                    "observaciones": observaciones_conductor,
                    # estos 3 empiezan vacíos, se llenan con
                    # asignar_tutor() / asignar_supervisor()
                    "tutor": None,
                    "supervisa_a": [],
                    "supervisor": None
                },
 
                # se va llenando con cada lectura de sensor (opción 2)
                "telemetria_iot": []
            }
 
            self.coleccion.insert_one(documento)
            return True, f"Viaje '{codigo_ruta}' creado con éxito."
 
        except (ValueError, TypeError):
            # esto salta si algún número (peso, año, capacidad, tiempo)
            # no se pudo convertir correctamente
            return False, "Alguno de los datos numéricos ingresados no es válido."
        except Exception as e:
            print(f"[ERROR interno en crear_viaje] {e}")
            return False, "Ocurrió un error inesperado al crear el viaje."
 

    # Consultas (leer datos)

    def existe_ruta(self, codigo_ruta):
        if not codigo_ruta:
            return False
        try:
            return self.coleccion.count_documents({"codigo_ruta": codigo_ruta}) > 0
        except Exception as e:
            print(f"[ERROR interno en existe_ruta] {e}")
            return False
 
    def obtener_viaje(self, codigo_ruta):
        if not codigo_ruta:
            return None
        try:
            return self.coleccion.find_one({"codigo_ruta": codigo_ruta})
        except Exception as e:
            print(f"[ERROR interno en obtener_viaje] {e}")
            return None
 
    def listar_viajes(self):
        try:
            cursor = self.coleccion.find(
                {},
                {"codigo_ruta": 1, "origen": 1, "destino": 1, "estado_viaje": 1, "_id": 0}
            )
            return list(cursor)
        except Exception as e:
            print(f"[ERROR interno en listar_viajes] {e}")
            return []
 
    def obtener_combustible_viaje(self, codigo_ruta):
        # actualizar_telemetria necesita esto para calcular consumo
        # y emisiones automáticamente
        viaje = self.obtener_viaje(codigo_ruta)
        if viaje:
            return viaje.get("tipo_combustible", "Diesel")
        return "Diesel"
 
    def obtener_alertas_activas(self):
        # Cada lectura de telemetría puede traer una lista de alertas
        # puede haber más de una alerta en la misma lectura. 
        alertas_encontradas = []
        try:
            cursor = self.coleccion.find({"telemetria_iot.alertas.0": {"$exists": True}})
            for viaje in cursor:
                for lectura in viaje.get("telemetria_iot", []):
                    for alerta in lectura.get("alertas", []):
                        alertas_encontradas.append({
                            "codigo_ruta": viaje.get("codigo_ruta"),
                            "alerta": alerta,
                            "timestamp": lectura.get("timestamp")
                        })
        except Exception as e:
            print(f"[ERROR interno en obtener_alertas_activas] {e}")
 
        return alertas_encontradas
 
    # ---------------------------------------------------------
    # Actualizar telemetría (cada vez que llega una lectura del sensor)
    # ---------------------------------------------------------
    def actualizar_telemetria(self, codigo_ruta, datos_sensores):
        if not datos_sensores or not isinstance(datos_sensores, dict):
            return False, "No se pudo actualizar: los datos del sensor no son válidos."
 
        if not codigo_ruta:
            return False, "Debes indicar un código de ruta."
 
        if not self.existe_ruta(codigo_ruta):
            return False, f"No existe ningún viaje con el código '{codigo_ruta}'."
 
        try:
            tipo_combustible = self.obtener_combustible_viaje(codigo_ruta)
 
            km = float(datos_sensores.get("km_recorridos", 0))
            if km < 0:
                return False, "Los kilómetros no pueden ser negativos."
 
            # el consumo de litros ya NO se pide al usuario, se calcula
            # solo a partir de los km recorridos y el tipo de combustible
            factor_consumo = self.FACTORES_CONSUMO.get(tipo_combustible, 0.2)
            litros = round(km * factor_consumo, 2)
 
            factor_emision = self.FACTORES_EMISION.get(tipo_combustible, 2.68)
            co2_kg = round(litros * factor_emision, 2)
 
            lat = float(datos_sensores.get("latitud", 0))
            lon = float(datos_sensores.get("longitud", 0))
            velocidad = float(datos_sensores.get("velocidad_kmh", 0))
            temp_motor = float(datos_sensores.get("temperatura_motor_c", 0))
            nivel_combustible = float(datos_sensores.get("nivel_combustible_pct", 0))
            alertas = datos_sensores.get("alertas", [])
 
            if not isinstance(alertas, list):
                alertas = [alertas] if alertas else []
 
            lectura = {
                "timestamp": datetime.now(),
                "km_recorridos": km,
                "litros_consumidos": litros,
                "emision_co2_kg": co2_kg,
                "coordenadas": {"latitud": lat, "longitud": lon},
                "velocidad_kmh": velocidad,
                "temperatura_motor_c": temp_motor,
                "nivel_combustible_pct": nivel_combustible,
                "alertas": alertas
            }
 
            self.coleccion.update_one(
                {"codigo_ruta": codigo_ruta},
                {"$push": {"telemetria_iot": lectura}}
            )
 
            return True, (
                f"Telemetría guardada para la ruta '{codigo_ruta}'. "
                f"Consumo calculado: {litros} L, CO2: {co2_kg} kg."
            )
 
        except (ValueError, TypeError):
            return False, "Los datos de telemetría deben ser números válidos."
        except Exception as e:
            print(f"[ERROR interno en actualizar_telemetria] {e}")
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
            print(f"[ERROR interno en eliminar_viaje] {e}")
            return False, "Ocurrió un error inesperado al eliminar el viaje."
 
 
    
    # Jerarquía de conductores (tutor / supervisor)
    def asignar_tutor(self, rut_novato, rut_tutor):
        # Un conductor experimentado (tutor) queda a cargo de uno o
        # varios conductores novatos.
        if not rut_novato or not rut_tutor:
            return False, "Debes indicar el RUT del novato y del tutor."
 
        if rut_novato == rut_tutor:
            return False, "Un conductor no puede ser tutor de sí mismo."
 
        try:
            novato_existe = self.coleccion.count_documents({"conductor.rut_id": rut_novato}) > 0
            tutor_existe = self.coleccion.count_documents({"conductor.rut_id": rut_tutor}) > 0
 
            if not novato_existe or not tutor_existe:
                return False, "No se encontró el conductor novato o el tutor."
 
            #  uso update_many, no update_one, porque el mismo
            # conductor puede aparecer en más de un viaje
            self.coleccion.update_many(
                {"conductor.rut_id": rut_novato},
                {"$set": {"conductor.tutor": rut_tutor}}
            )
            self.coleccion.update_many(
                {"conductor.rut_id": rut_tutor},
                {"$addToSet": {"conductor.supervisa_a": rut_novato}}
            )
 
            return True, f"El conductor {rut_tutor} ahora supervisa a {rut_novato}."
 
        except Exception as e:
            print(f"[ERROR interno en asignar_tutor] {e}")
            return False, "Error interno al asignar el tutor."
 
    def asignar_supervisor(self, rut_conductor, id_jefe_flota):
        # Un jefe de flota regional queda como supervisor de un conductor.
        if not rut_conductor or not id_jefe_flota:
            return False, "Debes indicar el RUT del conductor y el ID del jefe de flota."
 
        try:
            existe = self.coleccion.count_documents({"conductor.rut_id": rut_conductor}) > 0
            if not existe:
                return False, "No se encontró el conductor."
 
            self.coleccion.update_many(
                {"conductor.rut_id": rut_conductor},
                {"$set": {"conductor.supervisor": id_jefe_flota}}
            )
 
            return True, f"El conductor {rut_conductor} ahora está bajo supervisión del jefe {id_jefe_flota}."
 
        except Exception as e:
            print(f"[ERROR interno en asignar_supervisor] {e}")
            return False, "Error interno al asignar el supervisor."
 
 
 
    # Reporte de huella de carbono
    def obtener_reporte_carbono(self):
        # Consolida, por vehículo (patente), el total de kilómetros,
        # litros y CO2 emitido en todo el periodo, en kilogramos.
        try:
            pipeline = [
                {"$unwind": "$telemetria_iot"},
                {
                    "$group": {
                        "_id": "$vehiculo.patente",
                        "total_km": {"$sum": "$telemetria_iot.km_recorridos"},
                        "total_litros": {"$sum": "$telemetria_iot.litros_consumidos"},
                        "total_co2_kg": {"$sum": "$telemetria_iot.emision_co2_kg"}
                    }
                },
                {"$sort": {"total_co2_kg": -1}}
            ]
 
            resultados = list(self.coleccion.aggregate(pipeline))
 
            # redondeo los números para que el reporte se vea más limpio
            for fila in resultados:
                fila["total_km"] = round(fila.get("total_km", 0), 2)
                fila["total_litros"] = round(fila.get("total_litros", 0), 2)
                fila["total_co2_kg"] = round(fila.get("total_co2_kg", 0), 2)
 
            return resultados
 
        except Exception as e:
            print(f"[ERROR interno en obtener_reporte_carbono] {e}")
            return []
 
 
    # Cerrar la conexión al salir del programa
    def cerrar_conexion(self):
        try:
            self.client.close()
            print("Conexión a MongoDB cerrada.")
        except Exception as e:
            print(f"ERROR interno al cerrar conexión {e}")
 