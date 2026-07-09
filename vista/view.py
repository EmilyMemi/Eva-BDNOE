class VistaConsole:
    """
    mostrar información y capturar datos del usuario
    por consola. No contiene lógica de negocio ni acceso a base de datos.
    """
 
   
    # Menu principal y mensajes generales
 
    def mostrar_menu(self):
        print("\n" + "=" * 55)
        print(" " * 15 + "SISTEMA LOGITRACK_GLOBAL")
        print("=" * 55)
        print(" 1. Registrar nuevo viaje (vehículo + conductor + ruta)")
        print(" 2. Registrar lectura de telemetría (sensores IoT)")
        print(" 3. Ver alertas activas")
        print(" 4. Ver reporte de sostenibilidad (huella de carbono)")
        print(" 5. Ejecutar pruebas de diagnóstico (Tests)")
        print(" 6. Asignar tutor a un conductor novato")
        print(" 7. Asignar supervisor (jefe de flota) a un conductor")
        print(" 8. Salir")
        print("=" * 55)
        return input(" Seleccione una opción: ")
 
    def mostrar_mensaje(self, mensaje):
        print(f"\n  {mensaje}")
 
   
    # Opcion 1: Registrar nuevo viaje
    def solicitar_datos_viaje(self):
        """
        Solicita los datos necesarios para registrar un nuevo viaje.
        Retorna un diccionario ANIDADO (vehiculo, conductor,
        centro_contacto), que es el formato que espera crear_viaje()
        en modelo/models.py.
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
            peso_mercancia_kg = float(input("   Peso de la mercancía a transportar (Kg): "))
            tipo_combustible = input("   Tipo de combustible (Diesel/Gasolina/GNC/GLP/Híbrido): ")
 
            print("\n [Centro de Contacto de Despacho]")
            nombre_contacto = input("   Nombre del contacto: ")
            telefono_contacto = input("   Teléfono: ")
            email_contacto = input("   Email: ")
 
            print("\n [Datos del Vehículo]")
            vin = input("   VIN del vehículo: ")
            patente = input("   Patente: ")
            marca = input("   Marca: ")
            modelo_vehiculo = input("   Modelo: ")
            ano_fabricacion = int(input("   Año de fabricación: "))
            capacidad_carga = float(input("   Capacidad de carga MÁXIMA del vehículo (Kg): "))
            observaciones_vehiculo = input("   Observaciones mecánicas (Enter si no hay): ")
 
            print("\n [Datos del Conductor]")
            rut_id = input("   RUT/ID del conductor: ")
            nombre = input("   Nombre: ")
            primer_apellido = input("   Primer apellido: ")
            nacionalidad = input("   Nacionalidad: ")
            tipo_licencia = input("   Tipo de licencia (A1/A2/A3/B/C/D/E/F): ")
            fecha_vencimiento = input("   Fecha de vencimiento de la licencia (AAAA-MM-DD): ")
            observaciones_conductor = input("   Observaciones de desempeño (Enter si no hay): ")
 
            return {
                "codigo_ruta": codigo_ruta,
                "origen": origen,
                "destino": destino,
                "tiempo_estimado_dias": tiempo_estimado_dias,
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
                    "capacidad_carga_max_Kg": capacidad_carga,
                    "observaciones": observaciones_vehiculo
                },
 
                "conductor": {
                    "rut_id": rut_id,
                    "nombre": nombre,
                    "primer_apellido": primer_apellido,
                    "nacionalidad": nacionalidad,
                    "tipo_licencia": tipo_licencia,
                    "fecha_vencimiento": fecha_vencimiento,
                    # las capacitaciones no se piden por consola todavía,
                    # el viaje se crea con la lista vacía y se puede
                    # completar más adelante directo en Mongo si se necesita
                    "capacitaciones": [],
                    "observaciones": observaciones_conductor
                }
            }
        except ValueError:
            self.mostrar_mensaje("ERROR: Dato inválido ingresado. Se cancela el registro del viaje.")
            return None
        
        
    # Opcion 2: Telemetria (sensores IoT)
    def solicitar_codigo_ruta(self):
        return input("\n Ingrese el código de la ruta a actualizar: ")
 
    def solicitar_datos_telemetria(self):
        """
        Modelo los calcula automáticamente a partir de los kilómetros
        recorridos y el tipo de combustible del vehículo.
        """
        print("\n" + "-" * 45)
        print(" REGISTRO DE LECTURA DE TELEMETRÍA")
        print("-" * 45)
        try:
            latitud = float(input("   Latitud actual: "))
            longitud = float(input("   Longitud actual: "))
            velocidad_kmh = float(input("   Velocidad (km/h): "))
            temperatura_motor_c = float(input("   Temperatura del motor (°C): "))
            nivel_combustible_pct = float(input("   Nivel de combustible (%): "))
            km_recorridos = float(input("   Kilómetros recorridos desde última lectura: "))
            alerta = input("   Alerta del sistema (Enter si no hay ninguna): ").strip()
 
            return {
                "latitud": latitud,
                "longitud": longitud,
                "velocidad_kmh": velocidad_kmh,
                "temperatura_motor_c": temperatura_motor_c,
                "nivel_combustible_pct": nivel_combustible_pct,
                "km_recorridos": km_recorridos,
                "alertas": [alerta] if alerta else []
            }
        except ValueError:
            self.mostrar_mensaje("ERROR Dato inválido ingresado. Se cancela el registro de telemetría.")
            return None
 
    # Opcion 3: Alertas Activas
    def mostrar_alertas(self, alertas):
        """
        Muestra las alertas activas del sistema. 
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
            timestamp_texto = str(timestamp)[:19] if timestamp else "-"
            print(f" {str(a.get('codigo_ruta', '-')):<18}"
                  f"{str(a.get('alerta', '-')):<22}"
                  f"{timestamp_texto:<20}")
        print("=" * 60)
 
    # Opcion 4: Reporte de Sostenibilidad (osea Huella de Carbono)
    def mostrar_reporte_sostenibilidad(self, reporte_co2):
        """
        Muestra el reporte consolidado de emisiones de CO2, en
        kilogramos, con un resumen por cada vehículo (patente).
        """
        if not reporte_co2:
            print("\n No hay datos suficientes para generar el reporte de sostenibilidad.")
            return
 
        print("\n" + "=" * 60)
        print(" REPORTE DE SOSTENIBILIDAD (Huella de Carbono)")
        print("=" * 60)
        print(f" {'Patente':<12}{'Km totales':<14}{'Litros':<12}{'CO2 (kg)':<12}")
        print("-" * 60)
 
        total_km = 0
        total_litros = 0
        total_co2_kg = 0
 
        for fila in reporte_co2:
            patente = fila.get("_id", "Sin patente")
            km = fila.get("total_km", 0)
            litros = fila.get("total_litros", 0)
            co2_kg = fila.get("total_co2_kg", 0)
 
            print(f" {str(patente):<12}{km:<14}{litros:<12}{co2_kg:<12}")
 
            total_km += km
            total_litros += litros
            total_co2_kg += co2_kg
 
        print("-" * 60)
        print(f" {'TOTAL FLOTA':<12}{round(total_km, 2):<14}{round(total_litros, 2):<12}{round(total_co2_kg, 2):<12}")
        print("=" * 60)
 
 
    # Opcion 6 y 7: Jerarquía de conductores
    def solicitar_datos_tutor(self):
        print("\n" + "-" * 45)
        print(" ASIGNAR TUTOR A CONDUCTOR NOVATO")
        print("-" * 45)
        rut_novato = input("   RUT del conductor novato: ").strip()
        rut_tutor = input("   RUT del conductor tutor: ").strip()
        return rut_novato, rut_tutor
 
    def solicitar_datos_supervisor(self):
        print("\n" + "-" * 45)
        print(" ASIGNAR SUPERVISOR (JEFE DE FLOTA)")
        print("-" * 45)
        rut_conductor = input("   RUT del conductor: ").strip()
        id_jefe_flota = input("   ID del jefe de flota regional: ").strip()
        return rut_conductor, id_jefe_flota
 