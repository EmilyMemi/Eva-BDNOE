import unittest
from modelo.models import LogiTrackModel
from vista.view import VistaConsole
from test.test_logitrack import TestSistemaFlota

class ControladorLogistica:
    def __init__(self):
        self.vista = VistaConsole()
        try:
            self.modelo = LogiTrackModel()
        except ConnectionError as e:
            self.vista.mostrar_mensaje(f"ERROR CRÍTICO: {e}")
            raise SystemExit(1)

    def iniciar(self):
        while True:
            opcion = self.vista.mostrar_menu()

            if opcion == "1":
                # Crear viaje
                datos_viaje = self.vista.solicitar_datos_viaje()
                exito, msg = self.modelo.crear_viaje(datos_viaje)
                self.vista.mostrar_mensaje(msg)

            elif opcion == "2":
                # Actualizar telemetría
                codigo_ruta = self.vista.solicitar_codigo_ruta()
                if self.modelo.existe_ruta(codigo_ruta):
                    datos_sensores = self.vista.solicitar_datos_telemetria()
                    if datos_sensores:
                        exito, msg = self.modelo.actualizar_telemetria(codigo_ruta, datos_sensores)
                        self.vista.mostrar_mensaje(msg)
                else:
                    self.vista.mostrar_mensaje("Error: El código de ruta no existe.")

            elif opcion == "3":
                # Ver alertas activas
                alertas = self.modelo.obtener_alertas_activas()
                self.vista.mostrar_alertas(alertas)

            elif opcion == "4":
                # Reporte de sostenibilidad
                reporte_co2 = self.modelo.obtener_reporte_carbono()
                self.vista.mostrar_reporte_sostenibilidad(reporte_co2)

            elif opcion == "5":
                # Ejecutar pruebas de diagnóstico
                print("\n========================================================")
                print("      EJECUTANDO SUITE DE PRUEBAS AUTOMATIZADAS LOGITRACK   ")
                print("========================================================")
                suite = unittest.TestLoader().loadTestsFromTestCase(TestSistemaFlota)
                unittest.TextTestRunner(verbosity=2).run(suite)
                print("========================================================")

            elif opcion == "6":
                # Asignar tutor a conductor novato
                rut_novato, rut_tutor = self.vista.solicitar_datos_tutor()
                exito, msg = self.modelo.asignar_tutor(rut_novato, rut_tutor)
                self.vista.mostrar_mensaje(msg)

            elif opcion == "7":
                # Asignar supervisor (jefe de flota)
                rut_conductor, id_jefe_flota = self.vista.solicitar_datos_supervisor()
                exito, msg = self.modelo.asignar_supervisor(rut_conductor, id_jefe_flota)
                self.vista.mostrar_mensaje(msg)

            elif opcion == "8":
                # Salir
                self.vista.mostrar_mensaje("Cerrando conexiones y saliendo del sistema...")
                self.modelo.cerrar_conexion()
                break

            else:
                self.vista.mostrar_mensaje("Opción no válida. Intente nuevamente.")