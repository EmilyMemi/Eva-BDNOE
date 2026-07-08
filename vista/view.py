class VistaConsole:
    """
    contenedor que agrupa todos los métodos que vienen después
    """
 
    # ------------------------------------------------------------------
    # Menu principal y mensajes generales
 
    def mostrar_menu(self):
        print("\n" + "=" * 55)
        print("            SISTEMA LOGITRACK_GLOBAL")
        print("=" * 55)
        print(" 1. Registrar nuevo viaje (vehículo + conductor + ruta)")
        print(" 2. Registrar lectura de telemetría (sensores IoT)")
        print(" 3. Ver alertas activas")
        print(" 4. Ver reporte de sostenibilidad (huella de carbono)")
        print(" 5. Ejecutar pruebas de diagnóstico (Tests)")
        print(" 6. Salir")
        print("=" * 55)
        return input(" Seleccione una opción: ")
 
    def mostrar_mensaje(self, mensaje):
        print(f"\n  {mensaje}")
 
    # ------------------------------------------------------------------
    # Opcion 1: Registrar nuevo viaje
    def solicitar_datos_viaje(self):
        """
        Solicita los datos necesarios para registrar un nuevo viaje.
        Retorna un diccionario con la estructura acordada con el Modelo.
        """
        print("\n" + "-" * 45)
        print(" REGISTRO DE NUEVO VIAJE")
        print("-" * 45)
        try:
            print("\n [Datos de la Ruta]")
            codigo_ruta = input("   Código de ruta: ")
            origen = input("   Ciudad de origen: ")
            destino = input("   Ciudad de destino: ")
            tiempo_estimado_dias = float(input("   Tiempo estimado (días): "))
 
            print("\n [Datos del Vehículo]")
            vin = input("   VIN del vehículo: ")
            patente = input("   Patente: ")
            marca = input("   Marca: ")
            modelo_vehiculo = input("   Modelo: ")
            ano_fabricacion = int(input("   Año de fabricación: "))
            tipo_combustible = input("   Tipo de combustible (Diesel/Gasolina/GNC/GLP/Híbrido): ")
            capacidad_carga = float(input("   Capacidad de carga máxima (Kg): "))
 
            print("\n [Datos del Conductor]")
            rut_id = input("   RUT/ID del conductor: ")
            nombre = input("   Nombre: ")
            primer_apellido = input("   Primer apellido: ")
 
            return {
                "codigo_ruta": codigo_ruta,
                "origen": origen,
                "destino": destino,
                "tiempo_estimado_dias": tiempo_estimado_dias,
 
                # estas llaves planas son las que espera crear_viaje()
                # en modelo/models.py
                "patente_vehiculo": patente,
                "rut_conductor": rut_id,
                "nombre_conductor": f"{nombre} {primer_apellido}",
                "peso_mercancia_kg": capacidad_carga,
                "volumen_m3": 0,
                "tipo_combustible": tipo_combustible,
 
                # guardo el detalle completo del vehículo también,
                # por si más adelante se necesita mostrar el VIN o la marca
                "vin": vin,
                "marca": marca,
                "modelo_vehiculo": modelo_vehiculo,
                "ano_fabricacion": ano_fabricacion
            }
        except ValueError:
            self.mostrar_mensaje("ERROR: Dato inválido ingresado. Se cancela el registro del viaje.")
            return None
        
        
    # Opcion 2: Telemetria (sensores IoT)
    def solicitar_codigo_ruta(self):
        return input("\n Ingrese el código de la ruta a actualizar: ")
 
    def solicitar_datos_telemetria(self):
        """
        Solicita una lectura de sensores IoT para una ruta existente.
        Retorna un diccionario con los datos de telemetría, usando los
        mismos nombres de llave que espera actualizar_telemetria()
        en modelo/models.py.
        """
        print("\n" + "-" * 45)
        print(" REGISTRO DE LECTURA DE TELEMETRÍA")
        print("-" * 45)
        try:
            latitud = float(input("   Latitud actual: "))
            longitud = float(input("   Longitud actual: "))
            velocidad_kmh = float(input("   Velocidad (km/h): "))
            temperatura_motor_c = float(input("   Temperatura del motor (°C): "))
            nivel_combustible_porcentaje = float(input("   Nivel de combustible (%): "))
            km_recorridos = float(input("   Kilómetros recorridos desde última lectura: "))
            litros_consumidos = float(input("   Litros de combustible consumidos: "))
            alerta_sistema = input("   Alerta del sistema (Enter si no hay ninguna): ").strip()
 
            return {
                "ubicacion": {
                    "tipo": "Point",
                    "coordenadas": [longitud, latitud]
                },
                "velocidad_kmh": velocidad_kmh,
                "temperatura_motor_c": temperatura_motor_c,
                "nivel_combustible_porcentaje": nivel_combustible_porcentaje,
 
                #  estos dos nombres tienen que ser IDÉNTICOS a los
                # que lee actualizar_telemetria() en el modelo, si no
                "kilometros_recorridos_tramo": km_recorridos,
                "litros_consumidos": litros_consumidos,
                "alerta_sistema": alerta_sistema if alerta_sistema else None
            }
        except ValueError:
            self.mostrar_mensaje("ERROR: Dato inválido ingresado. Se cancela el registro de telemetría.")
            return None
 
    # ------------------------------------------------------------------
    # Opcion 3: Alertas Activas
    def mostrar_alertas(self, alertas):
        """
        Muestra las alertas activas del sistema.
        Se espera una lista de diccionarios como la que retorna
        obtener_alertas_activas() en modelo/models.py: cada uno con
        codigo_ruta, alerta y timestamp.
        """
        if not alertas:
            print("\n No hay alertas activas en este momento.")
            return
 
        print("\n" + "=" * 60)
        print(" ALERTAS ACTIVAS")
        print("=" * 60)
        print(f" {'Ruta':<18}{'Alerta':<22}{'Fecha / Hora':<20}")
        print("-" * 60)
        for a in alertas:
            timestamp = a.get("timestamp", "-")
            # si el timestamp viene como fecha completa, lo dejamos
            # más corto y legible en pantalla
            timestamp_texto = str(timestamp)[:19] if timestamp else "-"
            print(f" {str(a.get('codigo_ruta', '-')):<18}"
                  f"{str(a.get('alerta', '-')):<22}"
                  f"{timestamp_texto:<20}")
        print("=" * 60)
 

    # Opcion 4: Reporte de Sostenibilidad (osea Huella de Carbono)
    def mostrar_reporte_sostenibilidad(self, reporte_co2):
        """
        Muestra el reporte consolidado de emisiones de CO2.
        obtener_reporte_carbono() en modelo/models.py retorna una LISTA
        con un resumen por cada vehículo (patente), no un solo total.
        """
        if not reporte_co2:
            print("\n No hay datos suficientes para generar el reporte de sostenibilidad.")
            return
 
        print("\n" + "=" * 65)
        print(" REPORTE DE SOSTENIBILIDAD (Huella de Carbono)")
        print("=" * 65)
        print(f" {'Patente':<12}{'Km totales':<14}{'Litros':<12}{'CO2 (kg)':<12}{'CO2 (ton)':<10}")
        print("-" * 65)
 
        total_km = 0
        total_litros = 0
        total_co2_kg = 0
 
        for fila in reporte_co2:
            patente = fila.get("_id", "Sin patente")
            km = fila.get("total_km", 0)
            litros = fila.get("total_litros", 0)
            co2_kg = fila.get("total_co2_kg", 0)
            co2_ton = fila.get("total_co2_toneladas", 0)
 
            print(f" {str(patente):<12}{km:<14}{litros:<12}{co2_kg:<12}{co2_ton:<10}")
 
            total_km += km
            total_litros += litros
            total_co2_kg += co2_kg
 
        print("-" * 65)
        print(f" {'TOTAL FLOTA':<12}{total_km:<14}{total_litros:<12}{round(total_co2_kg, 2):<12}"
              f"{round(total_co2_kg / 1000, 4):<10}")
        print("=" * 65)
 