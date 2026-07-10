import unittest
from modelo.models import LogiTrackModel
from vista.view import VistaConsole
from test.test_logitrack import TestSistemaFlota
 
 
class ControladorLogistica:
    def __init__(self):
        self.vista = VistaConsole()
<<<<<<< HEAD
 
=======
        try:
            self.modelo = LogiTrackModel()
        except ConnectionError as e:
            self.vista.mostrar_mensaje(f"ERROR CRÍTICO: {e}")
            raise SystemExit(1)

>>>>>>> ef2fea4c6a7d59cab8868278c8f128e870cb7033
    def iniciar(self):
        try:
            self._loop_principal()
        except KeyboardInterrupt:
            self.vista.mostrar_mensaje("\nInterrumpido por el usuario (Ctrl+C). Cerrando conexiones...")
        except EOFError:
            self.vista.mostrar_mensaje("\nEntrada finalizada inesperadamente. Cerrando conexiones...")
        finally:
            self.modelo.cerrar_conexion()
 
    def _loop_principal(self):
        while True:
            categoria = self.vista.mostrar_menu()
 
            if categoria == "A":
                if self._submenu_viajes() == "SALIR":
                    break
 
            elif categoria == "B":
                self._submenu_reportes()
 
            elif categoria == "C":
                self._submenu_conductores()
 
            elif categoria == "D":
                if self._submenu_sistema() == "SALIR":
                    break
 
            else:
                self.vista.mostrar_mensaje("Categoría no válida. Intente nuevamente.")
 
    # Submenú A: Viajes y Telemetría
    def _submenu_viajes(self):
        while True:
            opcion = self.vista.mostrar_submenu_viajes()
 
            if opcion == "1":
                # Registrar nuevo viaje: si algo sale mal (código
                # duplicado, dato inválido), se vuelve a pedir el
                # formulario completo, sin salir de esta opción.
                while True:
                    datos_viaje = self.vista.solicitar_datos_viaje()
 
                    if datos_viaje is None:
                        if not self.vista.confirmar_reintentar():
                            break
                        continue
 
                    exito, msg = self.modelo.crear_viaje(datos_viaje)
                    self.vista.mostrar_mensaje(msg)
 
                    if exito or not self.vista.confirmar_reintentar():
                        break
 
            elif opcion == "2":
                # Actualizar telemetría
                while True:
                    codigo_ruta = self.vista.solicitar_codigo_ruta()
 
                    if not self.modelo.existe_ruta(codigo_ruta):
                        self.vista.mostrar_mensaje("Error: El código de ruta no existe.")
                        if not self.vista.confirmar_reintentar():
                            break
                        continue
 
                    datos_sensores = self.vista.solicitar_datos_telemetria()
                    if datos_sensores is None:
                        if not self.vista.confirmar_reintentar():
                            break
                        continue
 
                    exito, msg = self.modelo.actualizar_telemetria(codigo_ruta, datos_sensores)
                    self.vista.mostrar_mensaje(msg)
 
                    if exito or not self.vista.confirmar_reintentar():
                        break
 
            elif opcion == "3":
                # Ver alertas activas (solo lectura)
                alertas = self.modelo.obtener_alertas_activas()
                self.vista.mostrar_alertas(alertas)
 
            elif opcion == "4":
                # Listar viajes registrados (solo lectura)
                viajes = self.modelo.listar_viajes()
                self.vista.mostrar_viajes(viajes)
 
            elif opcion == "0":
                return "VOLVER"
 
            else:
                self.vista.mostrar_mensaje("Opción no válida. Intente nuevamente.")
 
    # Submenú B: Reportes
    def _submenu_reportes(self):
        while True:
            opcion = self.vista.mostrar_submenu_reportes()
 
            if opcion == "1":
                # Reporte de sostenibilidad (solo lectura)
                reporte_co2 = self.modelo.obtener_reporte_carbono()
                self.vista.mostrar_reporte_sostenibilidad(reporte_co2)
 
            elif opcion == "0":
                return "VOLVER"
 
            else:
                self.vista.mostrar_mensaje("Opción no válida. Intente nuevamente.")
 
    # Submenú C: Conductores (CRUD + jerarquía)
    def _submenu_conductores(self):
        while True:
            opcion = self.vista.mostrar_submenu_conductores()
 
            if opcion == "1":
                # Registrar nuevo conductor: cada campo se valida al
                # momento de ingresarlo, solo se re-pregunta el campo
                # que falló, no todo el formulario.
                datos_conductor = self.vista.solicitar_datos_conductor(
                    self.modelo.LICENCIAS_VALIDAS,
                    lambda rut: not self.modelo.existe_conductor(rut)
                )
                exito, msg = self.modelo.crear_conductor(datos_conductor)
                self.vista.mostrar_mensaje(msg)
 
            elif opcion == "2":
                # Listar conductores (solo lectura)
                conductores = self.modelo.listar_conductores()
                self.vista.mostrar_conductores(conductores)
 
            elif opcion == "3":
                # Ver detalle de un conductor
                while True:
                    rut_id = self.vista.solicitar_rut_conductor()
                    conductor = self.modelo.obtener_conductor(rut_id)
 
                    if conductor:
                        self.vista.mostrar_detalle_conductor(conductor)
                        break
 
                    self.vista.mostrar_mensaje(f"No se encontró ningún conductor con el RUT '{rut_id}'.")
                    if not self.vista.confirmar_reintentar():
                        break
 
            elif opcion == "4":
                # Actualizar datos de un conductor: el RUT y la licencia
                # se validan al momento de ingresarlos, solo se
                # re-pregunta el campo que falló.
                rut_id, datos_nuevos = self.vista.solicitar_datos_actualizar_conductor(
                    self.modelo.LICENCIAS_VALIDAS,
                    self.modelo.existe_conductor
                )
                exito, msg = self.modelo.actualizar_conductor(rut_id, datos_nuevos)
                self.vista.mostrar_mensaje(msg)
 
            elif opcion == "5":
                # Eliminar conductor
                while True:
                    rut_id = self.vista.solicitar_rut_conductor("RUT/ID del conductor a eliminar: ")
                    exito, msg = self.modelo.eliminar_conductor(rut_id)
                    self.vista.mostrar_mensaje(msg)
 
                    if exito or not self.vista.confirmar_reintentar():
                        break
 
            elif opcion == "6":
                # Asignar tutor a conductor novato: ambos RUT se
                # validan al momento de ingresarlos.
                rut_novato, rut_tutor = self.vista.solicitar_datos_tutor(self.modelo.existe_conductor)
                exito, msg = self.modelo.asignar_tutor(rut_novato, rut_tutor)
                self.vista.mostrar_mensaje(msg)
 
            elif opcion == "7":
                # Asignar supervisor (jefe de flota): el RUT del
                # conductor se valida al momento de ingresarlo.
                rut_conductor, id_jefe_flota = self.vista.solicitar_datos_supervisor(self.modelo.existe_conductor)
                exito, msg = self.modelo.asignar_supervisor(rut_conductor, id_jefe_flota)
                self.vista.mostrar_mensaje(msg)
 
            elif opcion == "0":
                return "VOLVER"
 
            else:
                self.vista.mostrar_mensaje("Opción no válida. Intente nuevamente.")
 
    # Submenú D: Sistema (tests / salir)
    def _submenu_sistema(self):
        while True:
            opcion = self.vista.mostrar_submenu_sistema()
 
            if opcion == "1":
                # Ejecutar pruebas de diagnóstico
                print("\n========================================================")
                print("      EJECUTANDO SUITE DE PRUEBAS AUTOMATIZADAS LOGITRACK   ")
                print("========================================================")
                suite = unittest.TestLoader().loadTestsFromTestCase(TestSistemaFlota)
                unittest.TextTestRunner(verbosity=2).run(suite)
                print("========================================================")
 
            elif opcion == "2":
                # Salir
                self.vista.mostrar_mensaje("Cerrando conexiones y saliendo del sistema...")
                return "SALIR"
 
            elif opcion == "0":
                return "VOLVER"
 
            else:
                self.vista.mostrar_mensaje("Opción no válida. Intente nuevamente.")
 
 