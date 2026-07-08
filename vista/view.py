class VistaConsole:
    """
    Capa de Vista (MVC) para el sistema LogiTrack_Global.
    Responsabilidad única: mostrar información y capturar datos del usuario
    por consola. No contiene lógica de negocio ni acceso a base de datos.
    """

    # ------------------------------------------------------------------
    # Menu principal y mensajes generales

    def mostrar_menu(self):
        print("\n=== Sistema LogiTrack_Global ===")
        print("1. Registrar nuevo viaje (vehículo + conductor + ruta)")
        print("2. Registrar lectura de telemetría (sensores IoT)")
        print("3. Ver alertas activas")
        print("4. Ver reporte de sostenibilidad (huella de carbono)")
        print("5. Listar viajes registrados")
        print("6. Actualizar viaje")
        print("7. Eliminar viaje")
        print("8. Ejecutar pruebas de diagnóstico (Tests)")
        print("9. Salir")
        return input("Seleccione una opción: ")


    def mostrar_mensaje(self, mensaje):
        print(f" {mensaje}")

    # ------------------------------------------------------------------
    # Opcion 1: Registrar nuevo viaje
    def solicitar_datos_viaje(self):
        """
        Solicita los datos necesarios para registrar un nuevo viaje.
        Retorna un diccionario con la estructura acordada con el Modelo.
        """
        print("\n--- Registro de nuevo viaje ---")
        try:
            print("\n[Datos de la Ruta]")
            codigo_ruta = input("Código de ruta: ")
            origen = input("Ciudad de origen: ")
            destino = input("Ciudad de destino: ")
            tiempo_estimado_dias = float(input("Tiempo estimado (dias): "))

            print("\n[Datos del Vehículo]")
            vin = input("VIN del vehículo: ")
            patente = input("Patente: ")
            marca = input("Marca: ")
            modelo_vehiculo = input("Modelo: ")
            ano_fabricacion = int(input("Año de fabricación: "))
            tipo_combustible = input("Tipo de combustible (Diesel/Gasolina/GNC/GLP/Híbrido): ")
            capacidad_carga = float(input("Capacidad de carga máxima (Kg): "))

            print("\n[Datos del Conductor]")
            rut_id = input("RUT/ID del conductor: ")
            nombre = input("Nombre: ")
            primer_apellido = input("Primer apellido: ")

            return {
                "codigo_ruta": codigo_ruta,
                "origen": origen,
                "destino": destino,
                "tiempo_estimado_dias": tiempo_estimado_dias,
                "vehiculo": {
                    "vin": vin,
                    "patente": patente,
                    "marca": marca,
                    "modelo": modelo_vehiculo,
                    "ano_fabricacion": ano_fabricacion,
                    "tipo_combustible": tipo_combustible,
                    "capacidad_carga_max_Kg": capacidad_carga
                },
                "conductor": {
                    "rut_id": rut_id,
                    "nombre": nombre,
                    "primer_apellido": primer_apellido
                }
            }
        except ValueError:
            self.mostrar_mensaje("Error:Dato invalido ingresado. Se cancela el registro del viaje.")
            return None

    # ------------------------------------------------------------------
    # Opcion 2: Telemetria (sensores IoT)
    def solicitar_codigo_ruta(self):
        return input("\nIngrese el código de la ruta: ")

    def solicitar_datos_telemetria(self):
    #    Solicita una lectura de sensores IoT para una ruta existente.
    # Retorna un diccionario con los datos de telemetría.
    
        print("\n--- Registro de lectura de telemetría ---")
        try:
            latitud = float(input("Latitud actual: "))
            longitud = float(input("Longitud actual: "))
            velocidad_kmh = float(input("Velocidad (km/h): "))
            temperatura_motor_c = float(input("Temperatura del motor (°C): "))
            nivel_combustible_porcentaje = float(input("Nivel de combustible (%): "))
            km_recorridos = float(input("Kilómetros recorridos desde última lectura: "))
            alerta_sistema = input("Alerta del sistema (Enter si no hay ninguna): ").strip()

            return {
                "ubicacion": {
                    "tipo": "Point",
                    "coordenadas": [longitud, latitud]
                },
                "velocidad_kmh": velocidad_kmh,
                "temperatura_motor_c": temperatura_motor_c,
                "nivel_combustible_porcentaje": nivel_combustible_porcentaje,
                "km_recorridos": km_recorridos,
                # litros_consumidos y emision_co2_kg se calculan en el modelo
                "alertas": alerta_sistema if alerta_sistema else None
            }
        except ValueError:
            self.mostrar_mensaje("Error: Dato inválido ingresado. Se cancela el registro de telemetria.")
            return {}


    # ------------------------------------------------------------------
    # Opcion 3: Alertas Activas
    def mostrar_alertas(self, alertas):
        """
        Muestra las alertas activas del sistema.
        Se espera una lista de diccionarios, cada uno con al menos:
        codigo_ruta, alerta_sistema y (opcional) datos de ubicación/velocidad.
        """
        if not alertas:
            print("\nNo hay alertas activas en este momento.")
            return

        print("\n=== ALERTAS ACTIVAS ===")
        print(f"{'Ruta':<20}{'Alerta':<20}{'Velocidad (km/h)':<18}")
        print("-" * 58)
        for a in alertas:
            print(f"{a.get('codigo_ruta', '-'):<20}"
                  f"{a.get('alerta_sistema', '-'):<20}"
                  f"{a.get('velocidad_kmh', '-'):<18}")

    # ------------------------------------------------------------------
    # Opcion 4: Reporte de Sostenibilidad (osea Huella de Carbono)
    def mostrar_reporte_sostenibilidad(self, reporte_co2):
        """
        Muestra el reporte consolidado de emisiones de CO2.
        Se espera un diccionario con totales generales, por ejemplo:
        {
            "total_km_recorridos": ...,
            "total_litros_consumidos": ...,
            "total_co2_kg": ...
        }
        """
        if not reporte_co2:
            print("\nNo hay datos suficientes para generar el reporte de sostenibilidad.")
            return

        print("\n=== REPORTE DE SOSTENIBILIDAD (Huella de Carbono) ===")
        print(f"Kilómetros totales recorridos : {reporte_co2.get('total_km_recorridos', 0)} km")
        print(f"Litros de combustible totales  : {reporte_co2.get('total_litros_consumidos', 0)} L")
        print(f"Emisión total de CO2           : {reporte_co2.get('total_co2_kg', 0)} kg")