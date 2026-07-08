import unittest
from modelo.models import LogiTrackModel
from vista.view import VistaConsole
from test.test_logitrack import TestSistemaFlota

class ControladorLogistica:
    def __init__(self):
        self.modelo = LogiTrackModel()
        self.vista = VistaConsole()
        
        # Factores de emisión oficiales (kg CO2 por litro)
        self.FACTORES_EMISION = {
            "Diesel": 2.68,
            "Gasolina": 2.35,
            "GNC": 2.72,
            "GLP": 1.66,
            "Híbrido": 1.45
        }

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
                    tipo_combustible = self.modelo.obtener_combustible_viaje(codigo_ruta)
                    co2_kg = self.calcular_huella_carbono(
                        tipo_combustible, 
                        datos_sensores.get("litros_consumidos", 0)
                    )
                    datos_sensores["emision_co2_kg"] = co2_kg
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
                # Listar viajes
                viajes = self.modelo.listar_viajes()
                if viajes:
                    print("\n=== LISTA DE VIAJES REGISTRADOS ===")
                    for v in viajes:
                        print(f"Ruta: {v.get('codigo_ruta','-')} | "
                              f"Origen: {v.get('origen','-')} | "
                              f"Destino: {v.get('destino','-')} | "
                              f"Estado: {v.get('estado_viaje','-')}")
                else:
                    self.vista.mostrar_mensaje("No hay viajes registrados.")

            elif opcion == "6":
                # Actualizar viaje (ejemplo: cambiar destino o estado)
                codigo_ruta = self.vista.solicitar_codigo_ruta()
                if self.modelo.existe_ruta(codigo_ruta):
                    nuevo_destino = input("Nuevo destino: ")
                    nuevo_estado = input("Nuevo estado del viaje: ")
                    exito, msg = self.modelo.actualizar_viaje(codigo_ruta, nuevo_destino, nuevo_estado)
                    self.vista.mostrar_mensaje(msg)
                else:
                    self.vista.mostrar_mensaje("Error: El código de ruta no existe.")

            elif opcion == "7":
                # Eliminar viaje
                codigo_ruta = self.vista.solicitar_codigo_ruta()
                exito, msg = self.modelo.eliminar_viaje(codigo_ruta)
                self.vista.mostrar_mensaje(msg)

            elif opcion == "8":
                # Ejecutar pruebas
                print("\n========================================================")
                print("      EJECUTANDO SUITE DE PRUEBAS AUTOMATIZADAS LOGITRACK   ") 
                print("========================================================")
                suite = unittest.TestLoader().loadTestsFromTestCase(TestSistemaFlota)
                unittest.TextTestRunner(verbosity=2).run(suite)
                print("========================================================") 

            elif opcion == "9":
                # Salir
                self.vista.mostrar_mensaje("Cerrando conexiones y saliendo del sistema...")
                self.modelo.cerrar_conexion()
                break

            else:
                self.vista.mostrar_mensaje("Opción no válida. Intente nuevamente.")

    def calcular_huella_carbono(self, tipo_combustible, litros_consumidos):
        factor = self.FACTORES_EMISION.get(tipo_combustible, 2.68)
        emisiones_kg = litros_consumidos * factor
        return round(emisiones_kg, 2)
