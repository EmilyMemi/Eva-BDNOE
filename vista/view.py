class VistaConsole:
    """
    No contiene lógica de negocio ni acceso a base de datos.
    """
 
   
    # Menu principal y submenús
    #
    # El menú se organizó en categorías para que sea más fácil de leer
    # y navegar. El controller.py usa las opciones de cada submenú
    def mostrar_menu(self):
        """Menú principal: solo categorías. Devuelve la letra elegida."""
        print("\n" + "=" * 55)
        print(" " * 15 + "SISTEMA LOGITRACK_GLOBAL")
        print("=" * 55)
        print(" A. Viajes y Telemetría")
        print(" B. Reportes")
        print(" C. Conductores (jerarquía)")
        print(" D. Sistema (pruebas / salir)")
        print("=" * 55)
        return input(" Seleccione una categoría: ").strip().upper()
 
    def mostrar_submenu_conductores(self):
        print("\n" + "-" * 55)
        print(" CONDUCTORES")
        print("-" * 55)
        print(" 1. Registrar nuevo conductor")
        print(" 2. Listar conductores")
        print(" 3. Ver detalle de un conductor")
        print(" 4. Actualizar datos de un conductor")
        print(" 5. Eliminar conductor")
        print(" 6. Asignar tutor a un conductor novato")
        print(" 7. Asignar supervisor (jefe de flota) a un conductor")
        print(" 0. Volver al menú principal")
        print("-" * 55)
        return input(" Seleccione una opción: ").strip()
    
 
    def mostrar_viajes(self, viajes):
        """
        Muestra la lista de viajes registrados
        No incluye todos los detalles del vehículo
        o conductor para no saturar la consola.
        """
        if not viajes:
            print("\n No hay viajes registrados todavía.")
            return
 
        print("\n" + "=" * 65)
        print(" VIAJES REGISTRADOS")
        print("=" * 65)
        print(f" {'Código Ruta':<18}{'Origen':<14}{'Destino':<14}{'Estado':<15}")
        print("-" * 65)
        for v in viajes:
            print(f" {str(v.get('codigo_ruta', '-')):<18}"
                  f"{str(v.get('origen', '-')):<14}"
                  f"{str(v.get('destino', '-')):<14}"
                  f"{str(v.get('estado_viaje', '-')):<15}")
        print("=" * 65)
 
    def mostrar_submenu_viajes(self):
        print("\n" + "-" * 55)
        print(" VIAJES Y TELEMETRÍA")
        print("-" * 55)
        print(" 1. Registrar nuevo viaje")
        print(" 2. Actualizar telemetría de un viaje")
        print(" 3. Ver alertas activas")
        print(" 4. Listar viajes registrados")
        print(" 0. Volver al menú principal")
        print("-" * 55)
        return input(" Seleccione una opción: ").strip()
    
    
    def mostrar_submenu_reportes(self):
        print("\n" + "-" * 55)
        print(" REPORTES")
        print("-" * 55)
        print(" 1. Ver reporte de sostenibilidad (huella de carbono)")
        print(" 0. Volver al menú principal")
        print("-" * 55)
        return input(" Seleccione una opción: ").strip()
 
 
    def mostrar_submenu_sistema(self):
        print("\n" + "-" * 55)
        print(" SISTEMA")
        print("-" * 55)
        print(" 1. Ejecutar pruebas de diagnóstico (Tests)")
        print(" 2. Salir del sistema")
        print(" 0. Volver al menú principal")
        print("-" * 55)
        return input(" Seleccione una opción: ").strip()
 
    def mostrar_mensaje(self, mensaje):
        print(f"\n  {mensaje}")
 
    def confirmar_reintentar(self):
        respuesta = input("\n ¿Desea intentarlo de nuevo? (s/n): ").strip().lower()
        return respuesta == "s"
    
    
    def _pedir_texto(self, prompt):
        return input(prompt).strip()
 
    def _pedir_numero(self, prompt):
        while True:
            valor = input(prompt).strip()
            try:
                return float(valor)
            except ValueError:
                print("   Valor inválido, debe ser un número. Intenta de nuevo.")
 
    def _pedir_opcion(self, prompt, opciones_validas):
        while True:
            valor = input(prompt).strip().upper()
            if valor in opciones_validas:
                return valor
            print(f"   Opción inválida. Usa una de estas: {', '.join(sorted(opciones_validas))}.")
            
            
    
    
    # Opcion 1: Registrar nuevo viaje
    def solicitar_datos_viaje(self):
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
            tipo_licencia = input("   Tipo de licencia (A1/A2/A3/A4/A5/B/C/D/E/F): ")
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
                    # el viaje se crea con la lista vacía 
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
 
 
 
    # Opciones 1 a 5: CRUD de conductores
    def solicitar_datos_conductor(self, licencias_validas, rut_disponible_fn):
        print("\n" + "-" * 45)
        print(" REGISTRO DE NUEVO CONDUCTOR")
        print("-" * 45)
 
        rut_id = self._pedir_texto("   RUT/ID del conductor: ")
        while not rut_id or not rut_disponible_fn(rut_id):
            print("   Ese RUT está vacío o ya existe. Ingresa otro.")
            rut_id = self._pedir_texto("   RUT/ID del conductor: ")
 
        nombre = self._pedir_texto("   Nombre: ")
        while not nombre:
            print("   El nombre no puede estar vacío.")
            nombre = self._pedir_texto("   Nombre: ")
 
        primer_apellido = self._pedir_texto("   Primer apellido: ")
        nacionalidad = self._pedir_texto("   Nacionalidad: ")
        tipo_licencia = self._pedir_opcion(
            "   Tipo de licencia (A1/A2/A3/A4/A5/B/C/D/E/F): ", licencias_validas
        )
        fecha_vencimiento = self._pedir_texto("   Fecha de vencimiento (AAAA-MM-DD): ")
        anos_experiencia = self._pedir_numero("   Años de experiencia: ")
        observaciones = self._pedir_texto("   Observaciones de desempeño (Enter si no hay): ")
 
        return {
            "rut_id": rut_id,
            "nombre": nombre,
            "primer_apellido": primer_apellido,
            "nacionalidad": nacionalidad,
            "tipo_licencia": tipo_licencia,
            "fecha_vencimiento": fecha_vencimiento,
            "anos_experiencia": anos_experiencia,
            "observaciones": observaciones
        }
 
    def mostrar_conductores(self, conductores):
        if not conductores:
            print("\n No hay conductores registrados todavía.")
            return
 
        print("\n" + "=" * 65)
        print(" CONDUCTORES REGISTRADOS")
        print("=" * 65)
        print(f" {'RUT/ID':<14}{'Nombre':<20}{'Licencia':<10}{'Tutor':<12}")
        print("-" * 65)
        for c in conductores:
            print(f" {str(c.get('rut_id', '-')):<14}"
                  f"{str(c.get('nombre', '-')):<20}"
                  f"{str(c.get('tipo_licencia', '-')):<10}"
                  f"{str(c.get('tutor', '-')):<12}")
        print("=" * 65)
 
    def solicitar_rut_conductor(self, mensaje="Ingrese el RUT/ID del conductor: "):
        return input(f"\n {mensaje}").strip()
 
    def mostrar_detalle_conductor(self, conductor):
        if not conductor:
            print("\n No se encontró ningún conductor con ese RUT.")
            return
 
        print("\n" + "=" * 55)
        print(" DETALLE DEL CONDUCTOR")
        print("=" * 55)
        print(f" RUT/ID:            {conductor.get('rut_id', '-')}")
        print(f" Nombre:            {conductor.get('nombre', '-')} {conductor.get('primer_apellido', '')}")
        print(f" Nacionalidad:      {conductor.get('nacionalidad', '-')}")
        print(f" Licencia:          {conductor.get('tipo_licencia', '-')}")
        print(f" Vence:             {conductor.get('fecha_vencimiento', '-')}")
        print(f" Años experiencia:  {conductor.get('anos_experiencia', '-')}")
        print(f" Observaciones:     {conductor.get('observaciones', '-')}")
        print(f" Tutor:             {conductor.get('tutor', '-')}")
        print(f" Supervisa a:       {conductor.get('supervisa_a', [])}")
        print(f" Supervisor:        {conductor.get('supervisor', '-')}")
        print("=" * 55)
 
    def solicitar_datos_actualizar_conductor(self, licencias_validas, conductor_existe_fn):
        print("\n" + "-" * 45)
        print(" ACTUALIZAR CONDUCTOR")
        print(" (deje en blanco y presione Enter para no modificar un campo)")
        print("-" * 45)
 
        rut_id = self._pedir_texto("   RUT/ID del conductor a actualizar: ")
        while not rut_id or not conductor_existe_fn(rut_id):
            print("   Ese RUT no existe. Ingresa uno válido.")
            rut_id = self._pedir_texto("   RUT/ID del conductor a actualizar: ")
 
        nombre = self._pedir_texto("   Nuevo nombre: ")
        primer_apellido = self._pedir_texto("   Nuevo primer apellido: ")
        nacionalidad = self._pedir_texto("   Nueva nacionalidad: ")
 
        tipo_licencia = input("   Nuevo tipo de licencia (Enter para no cambiar): ").strip().upper()
        while tipo_licencia and tipo_licencia not in licencias_validas:
            print(f"   Licencia inválida. Usa una de estas: {', '.join(sorted(licencias_validas))}.")
            tipo_licencia = input("   Nuevo tipo de licencia (Enter para no cambiar): ").strip().upper()
 
        fecha_vencimiento = self._pedir_texto("   Nueva fecha de vencimiento (AAAA-MM-DD): ")
 
        anos_experiencia_str = input("   Nuevos años de experiencia (Enter para no cambiar): ").strip()
        anos_experiencia = None
        while anos_experiencia_str:
            try:
                anos_experiencia = float(anos_experiencia_str)
                break
            except ValueError:
                print("   Valor inválido, debe ser un número.")
                anos_experiencia_str = input("   Nuevos años de experiencia (Enter para no cambiar): ").strip()
 
        observaciones = self._pedir_texto("   Nuevas observaciones: ")
 
        datos_nuevos = {
            "nombre": nombre,
            "primer_apellido": primer_apellido,
            "nacionalidad": nacionalidad,
            "tipo_licencia": tipo_licencia,
            "fecha_vencimiento": fecha_vencimiento,
            "observaciones": observaciones
        }
        if anos_experiencia is not None:
            datos_nuevos["anos_experiencia"] = anos_experiencia
 
        return rut_id, datos_nuevos
 
    
    
# Opcion 6 y 7: Jerarquía de conductores
    def solicitar_datos_tutor(self, conductor_existe_fn):
        print("\n" + "-" * 45)
        print(" ASIGNAR TUTOR A CONDUCTOR NOVATO")
        print("-" * 45)

        rut_novato = self._pedir_texto("   RUT del conductor novato: ")
        while not rut_novato or not conductor_existe_fn(rut_novato):
            print("   Ese RUT no existe. Ingresa uno válido.")
            rut_novato = self._pedir_texto("   RUT del conductor novato: ")

        rut_tutor = self._pedir_texto("   RUT del conductor tutor: ")
        while not rut_tutor or not conductor_existe_fn(rut_tutor) or rut_tutor == rut_novato:
            if rut_tutor == rut_novato:
                print("   Un conductor no puede ser tutor de sí mismo.")
            else:
                print("   Ese RUT no existe. Ingresa uno válido.")
            rut_tutor = self._pedir_texto("   RUT del conductor tutor: ")

        return rut_novato, rut_tutor

    def solicitar_datos_supervisor(self, conductor_existe_fn):
        print("\n" + "-" * 45)
        print("   ASIGNAR SUPERVISOR (JEFE DE FLOTA)")
        print("-" * 45)

        rut_conductor = self._pedir_texto("   RUT del conductor: ")

        while not rut_conductor or not conductor_existe_fn(rut_conductor):
            print("   Ese RUT no existe. Ingresa uno válido.")
            rut_conductor = self._pedir_texto("   RUT del conductor: ")

        id_jefe_flota = self._pedir_texto("   ID del jefe de flota regional: ")
        return rut_conductor, id_jefe_flota