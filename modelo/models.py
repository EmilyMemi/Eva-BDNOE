# actualizar la telemetría de los sensores, gestionar la jerarquía de
# conductores y sacar los reportes de CO2. El controller.py es el que
# llama a estas funciones, la vista nunca debería tocar este archivo
# directamente.
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, ConfigurationError
from datetime import datetime
<<<<<<< HEAD
from dotenv import load_dotenv
import os
import sys
=======
>>>>>>> ef2fea4c6a7d59cab8868278c8f128e870cb7033
 
# Cargamos las variables desde el archivo .env (si existe). Así la URI
# de conexión, el usuario, la contraseña y el nombre de la base de
# datos no quedan hardcodeados ni suben al repositorio (el .env está
# en el .gitignore).
load_dotenv()
 
 
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
    LICENCIAS_VALIDAS = {"A1", "A2", "A3", "A4", "A5", "B", "C", "D", "E", "F"}
 
    def __init__(self, uri=None, database_name=None):
        """
        Si el .env trae directamente MONGO_URI completo, se respeta
        ese valor (útil para MongoDB Atlas, que entrega la URI ya
        armada con su propio usuario de mínimo privilegio).
        """
        database_name = database_name or os.getenv("MONGO_DB_NAME", "logitrack_db")
        uri = uri or self._construir_uri(database_name)
 
        # serverSelectionTimeoutMS: no dejamos que la app se cuelgue
        # esperando indefinidamente si Mongo no está disponible.
        # tls: se activa solo si el .env lo pide explícitamente
        # (por ejemplo, para conectarse a un Atlas o a un servidor
        # remoto real); en un venv local con auth básica no hace falta.
        usar_tls = os.getenv("MONGO_TLS", "false").strip().lower() == "true"
 
        try:
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=3000,
                tls=usar_tls
            )
            self.client.server_info()  # esto "obliga" a probar la conexión ya
 
            self.db = self.client[database_name]
            self.coleccion = self.db["viajes_monitoreo"]
            self.coleccion_conductores = self.db["conductores"]
 
            print(f"Conectado a MongoDB sin problemas (base de datos: '{database_name}').")
 
        except OperationFailure:
            # Esto salta cuando el servidor SÍ respondió pero el
            # usuario/contraseña están mal, o el usuario no tiene
            # permisos sobre esa base de datos. OJO: nunca imprimimos
            # la URI completa acá porque trae la contraseña adentro.
            print("\n[ERROR] Usuario o contraseña incorrectos, o el usuario no "
                  "tiene permisos sobre la base de datos configurada.")
            print("Revisa MONGO_APP_USER / MONGO_APP_PASSWORD en tu archivo .env "
                  "y que el usuario tenga el rol readWrite sobre la base correcta.")
            sys.exit(1)
 
        except ServerSelectionTimeoutError:
            # El servidor no contestó a tiempo: puede que no esté
            # prendido, que el host/puerto estén mal, o que un
            # firewall esté bloqueando la conexión.
            print("\n[ERROR] No se pudo contactar al servidor de MongoDB.")
            print("Revisa que el servicio esté corriendo y que el host/puerto "
                  "en tu .env sean correctos.")
            sys.exit(1)
 
        except ConfigurationError as e:
            print(f"\n[ERROR] La configuración de conexión no es válida: {e}")
            print("Revisa el formato de las variables en tu archivo .env.")
            sys.exit(1)
 
        except Exception as e:
            print(f"\n[ERROR] No se pudo conectar a MongoDB: {e}")
<<<<<<< HEAD
            sys.exit(1)
=======
            print("Revisa que el servicio de MongoDB esté corriendo.")
            raise ConnectionError("No se pudo conectar a MongoDB. El programa no puede continuar.") from e
>>>>>>> ef2fea4c6a7d59cab8868278c8f128e870cb7033
 
    def _construir_uri(self, database_name):
        """
        Arma la URI de conexión a partir de variables de entorno
        separadas. Si el .env ya trae MONGO_URI completo, se usa
        directamente esa (útil para Atlas / entornos donde la URI
        viene dada). Si no, se construye con usuario y contraseña
        del usuario de mínimo privilegio (MONGO_APP_USER).
        """
        uri_completa = os.getenv("MONGO_URI")
        if uri_completa:
            return uri_completa
 
        host = os.getenv("MONGO_HOST", "localhost")
        puerto = os.getenv("MONGO_PORT", "27017")
        usuario = os.getenv("MONGO_APP_USER", "")
        password = os.getenv("MONGO_APP_PASSWORD", "")
        auth_source = os.getenv("MONGO_AUTH_SOURCE", database_name)
 
        if usuario and password:
            # authSource=logitrack_db porque el usuario de la app se
            # crea DENTRO de esa base, no en admin. Así, aunque alguien
            # obtenga estas credenciales, solo puede tocar esta base
            # de datos y nada más del servidor (principio de menor
            # privilegio).
            return (
                f"mongodb://{usuario}:{password}@{host}:{puerto}/"
                f"?authSource={auth_source}"
            )
 
        # Fallback sin autenticación, solo pensado para desarrollo
        # local rápido (por ejemplo, un Mongo recién instalado sin
        # auth activada todavía). En cualquier entorno real, siempre
        # debe usarse un usuario con permisos mínimos.
        print("[AVISO] No se encontraron credenciales (MONGO_APP_USER / "
              "MONGO_APP_PASSWORD) en el .env. Conectando sin autenticación, "
              "solo recomendado para desarrollo local.")
        return f"mongodb://{host}:{puerto}/"
 
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
 
        # Actualizar telemetría (cada vez que llega una lectura del sensor)
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
        # varios conductores novatos. Trabaja sobre la colección
        # maestra "conductores", no sobre los viajes.
        if not rut_novato or not rut_tutor:
            return False, "Debes indicar el RUT del novato y del tutor."

        if rut_novato == rut_tutor:
            return False, "Un conductor no puede ser tutor de sí mismo."

        try:
            if not self.existe_conductor(rut_novato) or not self.existe_conductor(rut_tutor):
                return False, "No se encontró el conductor novato o el tutor."

            self.coleccion_conductores.update_one(
                {"rut_id": rut_novato},
                {"$set": {"tutor": rut_tutor}}
            )
            self.coleccion_conductores.update_one(
                {"rut_id": rut_tutor},
                {"$addToSet": {"supervisa_a": rut_novato}}
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
            if not self.existe_conductor(rut_conductor):
                return False, "No se encontró el conductor."

            self.coleccion_conductores.update_one(
                {"rut_id": rut_conductor},
                {"$set": {"supervisor": id_jefe_flota}}
            )

            return True, f"El conductor {rut_conductor} ahora está bajo supervisión del jefe {id_jefe_flota}."

        except Exception as e:
            print(f"[ERROR interno en asignar_supervisor] {e}")
            return False, "Error interno al asignar el supervisor."
    # CRUD de la colección maestra "conductores"
    # ---------------------------------------------------------
    def crear_conductor(self, datos_conductor):
        # Alta de un conductor nuevo, independiente de si ya tiene
        # o no un viaje asignado.
        if not datos_conductor or not isinstance(datos_conductor, dict):
            return False, "No se pudo crear el conductor: los datos ingresados no son válidos."
 
        try:
            rut_id = str(datos_conductor.get("rut_id", "")).strip()
            nombre = str(datos_conductor.get("nombre", "")).strip()
            primer_apellido = str(datos_conductor.get("primer_apellido", "")).strip()
            nacionalidad = str(datos_conductor.get("nacionalidad", "")).strip()
            tipo_licencia = str(datos_conductor.get("tipo_licencia", "")).strip().upper()
            fecha_vencimiento_str = str(datos_conductor.get("fecha_vencimiento", "")).strip()
            anos_experiencia = datos_conductor.get("anos_experiencia", 0)
            observaciones = str(datos_conductor.get("observaciones", "")).strip()
 
            if not rut_id or not nombre:
                return False, "El RUT y el nombre del conductor son obligatorios."
 
            if self.existe_conductor(rut_id):
                return False, f"Ya existe un conductor con el RUT '{rut_id}'."
 
            if tipo_licencia and tipo_licencia not in self.LICENCIAS_VALIDAS:
                return False, (
                    f"Tipo de licencia inválido. Usa una de estas: "
                    f"{', '.join(sorted(self.LICENCIAS_VALIDAS))}."
                )
 
            anos_experiencia = float(anos_experiencia)
            if anos_experiencia < 0:
                return False, "Los años de experiencia no pueden ser negativos."
 
            documento = {
                "rut_id": rut_id,
                "nombre": nombre,
                "primer_apellido": primer_apellido,
                "nacionalidad": nacionalidad,
                "tipo_licencia": tipo_licencia,
                "fecha_vencimiento": fecha_vencimiento_str,
                "anos_experiencia": anos_experiencia,
                "observaciones": observaciones,
                # igual que en crear_viaje: empiezan vacíos, se llenan
                # con asignar_tutor() / asignar_supervisor()
                "tutor": None,
                "supervisa_a": [],
                "supervisor": None
            }
 
            self.coleccion_conductores.insert_one(documento)
            return True, f"Conductor '{nombre}' (RUT {rut_id}) creado con éxito."
 
        except (ValueError, TypeError):
            return False, "Los años de experiencia deben ser un número válido."
        except Exception as e:
            print(f"[ERROR interno en crear_conductor] {e}")
            return False, "Ocurrió un error inesperado al crear el conductor."
 
    def existe_conductor(self, rut_id):
        if not rut_id:
            return False
        try:
            return self.coleccion_conductores.count_documents({"rut_id": rut_id}) > 0
        except Exception as e:
            print(f"[ERROR interno en existe_conductor] {e}")
            return False
    def listar_conductores(self):
        # Trae todos los conductores registrados como entidad propia,
        # sin importar si ya tienen o no un viaje asignado.
        try:
            cursor = self.coleccion_conductores.find({}, {"_id": 0})
            return list(cursor)
        except Exception as e:
            print(f"[ERROR interno en listar_conductores] {e}")
            return []

    def obtener_conductor(self, rut_id):
        # Detalle de un solo conductor por su RUT/ID.
        if not rut_id:
            return None
        try:
            return self.coleccion_conductores.find_one({"rut_id": rut_id}, {"_id": 0})
        except Exception as e:
            print(f"[ERROR interno en obtener_conductor] {e}")
            return None
        
    def actualizar_conductor(self, rut_id, datos_nuevos):
        # Actualiza los datos propios del conductor (no la jerarquía:
        # eso se hace con asignar_tutor / asignar_supervisor).
        if not rut_id:
            return False, "Debes indicar el RUT del conductor a actualizar."

        if not datos_nuevos or not isinstance(datos_nuevos, dict):
            return False, "No se pudo actualizar: los datos ingresados no son válidos."

        if not self.existe_conductor(rut_id):
            return False, f"No existe ningún conductor con el RUT '{rut_id}'."

        try:
            campos_permitidos = [
                "nombre", "primer_apellido", "nacionalidad",
                "tipo_licencia", "fecha_vencimiento",
                "anos_experiencia", "observaciones"
            ]

            actualizacion = {}
            for campo in campos_permitidos:
                if campo in datos_nuevos and datos_nuevos[campo] not in (None, ""):
                    actualizacion[campo] = datos_nuevos[campo]

            if not actualizacion:
                return False, "No se ingresó ningún dato nuevo para actualizar."

            if "tipo_licencia" in actualizacion:
                actualizacion["tipo_licencia"] = str(actualizacion["tipo_licencia"]).strip().upper()
                if actualizacion["tipo_licencia"] not in self.LICENCIAS_VALIDAS:
                    return False, (
                        f"Tipo de licencia inválido. Usa una de estas: "
                        f"{', '.join(sorted(self.LICENCIAS_VALIDAS))}."
                    )

            if "anos_experiencia" in actualizacion:
                actualizacion["anos_experiencia"] = float(actualizacion["anos_experiencia"])
                if actualizacion["anos_experiencia"] < 0:
                    return False, "Los años de experiencia no pueden ser negativos."

            self.coleccion_conductores.update_one(
                {"rut_id": rut_id},
                {"$set": actualizacion}
            )

            return True, f"Conductor {rut_id} actualizado con éxito."

        except (ValueError, TypeError):
            return False, "Los años de experiencia deben ser un número válido."
        except Exception as e:
            print(f"[ERROR interno en actualizar_conductor] {e}")
            return False, "Ocurrió un error inesperado al actualizar el conductor."    


    def eliminar_conductor(self, rut_id):
        # Antes de eliminar, se limpia la jerarquía para no dejar
        # referencias "huérfanas" en otros conductores.
        if not rut_id:
            return False, "Debes indicar el RUT del conductor a eliminar."

        conductor = self.obtener_conductor(rut_id)
        if not conductor:
            return False, f"No existe ningún conductor con el RUT '{rut_id}'."

        try:
            tutor_actual = conductor.get("tutor")
            if tutor_actual:
                # Se lo saco de la lista de supervisados de su tutor.
                self.coleccion_conductores.update_one(
                    {"rut_id": tutor_actual},
                    {"$pull": {"supervisa_a": rut_id}}
                )

            supervisados = conductor.get("supervisa_a", [])
            if supervisados:
                # A los novatos que este conductor tutoraba, les quito
                # la referencia porque su tutor ya no va a existir.
                self.coleccion_conductores.update_many(
                    {"rut_id": {"$in": supervisados}},
                    {"$set": {"tutor": None}}
                )

            self.coleccion_conductores.delete_one({"rut_id": rut_id})
            return True, f"Conductor {rut_id} eliminado con éxito."

        except Exception as e:
            print(f"[ERROR interno en eliminar_conductor] {e}")
            return False, "Ocurrió un error inesperado al eliminar el conductor."




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
 