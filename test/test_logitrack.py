# Acá van las pruebas automáticas del sistema. La idea es no tener
# que probar todo a mano cada vez (crear un viaje, ver si quedó bien,
# borrarlo...) sino que el código lo haga solo y nos diga si algo
# se rompió.
# Uso un código de ruta bien raro para las pruebas (TEST-QA-999) así
# no se me mezcla con viajes reales que haya guardado antes.

import unittest
from modelo.models import LogiTrackModel


class TestSistemaFlota(unittest.TestCase):

    CODIGO_PRUEBA = "TEST-QA-999"

def setUp(self):
    try:
        # Base de datos separada, exclusiva para tests. Así nunca
        # tocamos la colección real de producción (logitrack_db).
        self.modelo = LogiTrackModel(database_name="logitrack_test_db")
    except ConnectionError as e:
        self.skipTest(f"Mongo no disponible: {e}")

    if self.modelo.existe_ruta(self.CODIGO_PRUEBA):
        self.modelo.eliminar_viaje(self.CODIGO_PRUEBA)

    def tearDown(self):
        # tearDown se ejecuta DESPUÉS de cada test, pase lo que pase.
        # Acá limpio el viaje de prueba para no dejar basura en Mongo.
        if self.modelo.existe_ruta(self.CODIGO_PRUEBA):
            self.modelo.eliminar_viaje(self.CODIGO_PRUEBA)
        self.modelo.cerrar_conexion()

    def datos_viaje_de_prueba(self):
        # Función chica para no repetir el mismo diccionario en cada test.
        # esto tiene que calzar con lo que espera crear_viaje() en
        # models.py, por eso va todo anidado (vehiculo, conductor, etc.)
        return {
            "codigo_ruta": self.CODIGO_PRUEBA,
            "origen": "Santiago",
            "destino": "Antofagasta",
            "tiempo_estimado_dias": 2,
            "peso_mercancia_kg": 1000,
            "tipo_combustible": "Diesel",

            "centro_contacto": {
                "nombre": "Contacto Prueba",
                "telefono": "912345678",
                "email": "prueba@logitrack.cl"
            },

            "vehiculo": {
                "vin": "1HGCM82633A123456",
                "patente": "AAAA-11",
                "marca": "Volvo",
                "modelo": "FH16",
                "ano_fabricacion": 2020,
                "capacidad_carga_max_Kg": 5000,
                "observaciones": ""
            },

            "conductor": {
                "rut_id": "11111111-1",
                "nombre": "Conductor",
                "primer_apellido": "De Prueba",
                "nacionalidad": "Chilena",
                "tipo_licencia": "A5",
                "fecha_vencimiento": "2027-01-01",
                "capacitaciones": [],
                "observaciones": ""
            }
        }

    def test_crear_viaje_exitoso(self):
        # Si mando datos válidos, se debería crear sin problema
        exito, msg = self.modelo.crear_viaje(self.datos_viaje_de_prueba())
        self.assertTrue(exito)
        self.assertTrue(self.modelo.existe_ruta(self.CODIGO_PRUEBA))

    def test_no_permite_codigo_duplicado(self):
        # Creo el viaje una vez (debería funcionar)
        self.modelo.crear_viaje(self.datos_viaje_de_prueba())

        # Intento crearlo de nuevo con el mismo código, esta vez
        # tiene que fallar
        exito, msg = self.modelo.crear_viaje(self.datos_viaje_de_prueba())
        self.assertFalse(exito)

    def test_rechaza_combustible_invalido(self):
        datos = self.datos_viaje_de_prueba()
        datos["tipo_combustible"] = "Kerosene"  # esto no está en la lista válida

        exito, msg = self.modelo.crear_viaje(datos)
        self.assertFalse(exito)

    def test_actualizar_telemetria(self):
        # Primero necesito que el viaje exista para poder actualizarlo
        self.modelo.crear_viaje(self.datos_viaje_de_prueba())

        lectura_sensor = {
            "km_recorridos": 120,
            "latitud": -33.45,
            "longitud": -70.65,
            "velocidad_kmh": 80,
            "temperatura_motor_c": 90,
            "nivel_combustible_pct": 75,
            "alertas": []
        }

        exito, msg = self.modelo.actualizar_telemetria(self.CODIGO_PRUEBA, lectura_sensor)
        self.assertTrue(exito)

        # reviso que la lectura haya quedado guardada dentro del viaje
        viaje = self.modelo.obtener_viaje(self.CODIGO_PRUEBA)
        self.assertEqual(len(viaje["telemetria_iot"]), 1)

    def test_no_actualiza_telemetria_de_ruta_inexistente(self):
        lectura_sensor = {
            "km_recorridos": 50,
            "latitud": -33.45,
            "longitud": -70.65,
            "velocidad_kmh": 60,
            "temperatura_motor_c": 85,
            "nivel_combustible_pct": 60,
            "alertas": []
        }
        exito, msg = self.modelo.actualizar_telemetria("RUTA-QUE-NO-EXISTE", lectura_sensor)
        self.assertFalse(exito)

    def test_eliminar_viaje(self):
        self.modelo.crear_viaje(self.datos_viaje_de_prueba())
        exito, msg = self.modelo.eliminar_viaje(self.CODIGO_PRUEBA)
        self.assertTrue(exito)
        self.assertFalse(self.modelo.existe_ruta(self.CODIGO_PRUEBA))


if __name__ == "__main__":
    unittest.main()