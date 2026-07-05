import unittest
from modelo.models import LogiTrackModel
from vista.view import VistaConsole
from test.test_logitrack import TestSistemaFlota

class ControladorLogistica:
    def __init__(self):
        self.modelo = LogiTrackModel()
        self.vista = VistaConsole()
        
        # 3. FACTORES DE EMISIÓN OFICIALES (Ejemplos basados en MITECO / kg CO2 por Litro)
        self.FACTORES_EMISION = {
            "Diesel": 2.68,
            "Gasolina": 2.35,
            "GNC": 2.72,  # Por kg
            "GLP": 1.66,
            "Híbrido": 1.45 # Factor reducido estimado
        }

    def iniciar(self):
        while True:
            opcion = self.vista.mostrar_menu()
            
            if opcion == "1":
                # Alta de viaje (incluye tipo de combustible, peso mercancía, etc.)
                datos_viaje = self.vista.solicitar_datos_viaje()
                exito, msg = self.modelo.crear_viaje(datos_viaje)
                self.vista.mostrar_mensaje(msg)

            elif opcion == "2":
                # 1. RECOPILAR DATOS DE ACTIVIDAD DESDE LA VISTA
                codigo_ruta = self.vista.solicitar_codigo_ruta()
                
                if self.modelo.existe_ruta(codigo_ruta):
                    # La vista ahora pide: litros_consumidos, km_recorridos y alertas
                    datos_sensores = self.vista.solicitar_datos_telemetria()
                    
                    # Obtenemos el tipo de combustible de este viaje desde el modelo
                    tipo_combustible = self.modelo.obtener_combustible_viaje(codigo_ruta)
                    
                    # 4. CALCULAR LAS EMISIONES
                    co2_kg = self.calcular_huella_carbono(
                        tipo_combustible, 
                        datos_sensores.get("litros_consumidos", 0)
                    )
                    
                    # Guardamos el resultado del cálculo en los datos que irán a MongoDB
                    datos_sensores["emision_co2_kg"] = co2_kg
                    
                    # Guardar telemetría y huella en subdocumento (MongoDB $push)
                    exito, msg = self.modelo.actualizar_telemetria(codigo_ruta, datos_sensores)
                    self.vista.mostrar_mensaje(msg)
                else:
                    self.vista.mostrar_mensaje("Error: El código de ruta no existe.")

            elif opcion == "3":
                # Consultar alertas y estado
                alertas = self.modelo.obtener_alertas_activas()
                self.vista.mostrar_alertas(alertas)

            elif opcion == "4":
                # 5. CONSOLIDAR Y REPORTAR RESULTADOS (Estilo ISO 14083 / GHG Protocol)
                # El modelo usará agregaciones para sumar kilómetros, combustible y CO2 totales
                reporte_co2 = self.modelo.obtener_reporte_carbono()
                self.vista.mostrar_reporte_sostenibilidad(reporte_co2)

            elif opcion == "5":
                # Pruebas automatizadas (QA)
                print("\n========================================================")
                print("      EJECUTANDO SUITE DE PRUEBAS AUTOMATIZADAS LOGITRACK   ") 
                print("========================================================")
                suite = unittest.TestLoader().loadTestsFromTestCase(TestSistemaFlota)
                unittest.TextTestRunner(verbosity=2).run(suite)
                print("========================================================") 

            elif opcion == "6":
                self.vista.mostrar_mensaje("Cerrando conexiones y saliendo del sistema...")
                self.modelo.cerrar_conexion()
                break
            else:
                self.vista.mostrar_mensaje("Opción inválida. Reintente.")

    def calcular_huella_carbono(self, tipo_combustible, litros_consumidos):
        """
        Aplica la fórmula matemática oficial: Datos de Actividad x Factor de Emisión.
        """
        # Si el tipo de combustible no está registrado, usa Diesel por defecto (el más común en carga)
        factor = self.FACTORES_EMISION.get(tipo_combustible, 2.68)
        
        # Fórmula: Emisiones = Litros consumidos * Factor
        emisiones_kg = litros_consumidos * factor
        
        return round(emisiones_kg, 2)
