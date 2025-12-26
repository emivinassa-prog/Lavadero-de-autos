import json
import os
from datetime import datetime

# Archivo de datos
ARCHIVO_DATOS = "datos_lavadero_pro.json"

def guardar_datos(clientes, servicios, contador):
    data = {"clientes": clientes, "servicios": servicios, "contador": contador}
    with open(ARCHIVO_DATOS, "w") as f:
        json.dump(data, f, indent=4)

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r") as f:
            data = json.load(f)
            return data["clientes"], data["servicios"], data["contador"]
    return {}, [], 1

clientes, servicios, contador_id_lavado = cargar_datos()

def registrar_cliente():
    global clientes
    nombre = input("Nombre del cliente: ")
    telefono = input("Teléfono: ")
    ultimos_digitos = telefono[-4:] 
    vehiculos = [v.strip() for v in input("Vehículos (separados por coma): ").split(",")]
    
    clientes[ultimos_digitos] = {'nombre': nombre, 'telefono': telefono, 'vehiculos': vehiculos}
    guardar_datos(clientes, servicios, contador_id_lavado)
    print(f"✅ Cliente {nombre} registrado.")

def cargar_lavado():
    global contador_id_lavado, servicios
    busqueda = input("Últimos dígitos del teléfono: ")
    
    if busqueda not in clientes:
        print("❌ Cliente no encontrado."); return

    cliente = clientes[busqueda]
    
    # Selección Vehículo
    for i, v in enumerate(cliente['vehiculos'], 1): print(f"{i}. {v}")
    vehiculo_sel = cliente['vehiculos'][int(input("Seleccione vehículo: ")) - 1]

    # Tipo de Lavado
    opciones = ["Lavado básico", "Lavado a domicilio", "Limpieza de motor", "Ópticas", "Abrillantado", "Limpieza de tapizado"]
    for i, tipo in enumerate(opciones, 1): print(f"{i}. {tipo}")
    tipo_sel = opciones[int(input("Tipo de lavado: ")) - 1]

    # Valores
    valor = float(input("Valor del servicio: $"))
    propina = float(input("Propina: $"))

    # Método de Pago
    print("Método de pago: 1. Efectivo | 2. Mercado Pago")
    metodo_sel = "Efectivo" if input("Opción: ") == "1" else "Mercado Pago"

    # Ayudante
    ayudantes = ["No hubo", "Vicki", "Maxi", "Soto"]
    for i, ayu in enumerate(ayudantes, 1): print(f"{i}. {ayu}")
    ayu_sel = ayudantes[int(input("Ayudante: ")) - 1]
    pago_ayu = float(input(f"Pago para {ayu_sel}: $")) if ayu_sel != "No hubo" else 0

    # Fecha Actual Automática
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year

    registro = {
        'id': contador_id_lavado,
        'fecha': fecha_hoy,
        'mes': mes_actual,
        'anio': anio_actual,
        'cliente': cliente['nombre'],
        'vehiculo': vehiculo_sel,
        'tipo': tipo_sel,
        'valor': valor,
        'propina': propina,
        'metodo_pago': metodo_sel,
        'ayudante': ayu_sel,
        'pago_ayudante': pago_ayu
    }
    
    servicios.append(registro)
    print(f"✨ Lavado ID {contador_id_lavado} cargado el {fecha_hoy} ({metodo_sel}).")
    contador_id_lavado += 1
    guardar_datos(clientes, servicios, contador_id_lavado)

def eliminar_lavado():
    global servicios
    id_elim = int(input("ID del lavado a eliminar: "))
    servicios = [s for s in servicios if s['id'] != id_elim]
    guardar_datos(clientes, servicios, contador_id_lavado)
    print("🗑️ Registro eliminado.")

def mostrar_reporte():
    mes = int(input("Mes a consultar (1-12): "))
    anio = datetime.now().year
    
    efectivo = 0
    mercado_pago = 0
    total_propinas = 0
    pago_empleados = 0
    
    print(f"\n{'='*90}")
    print(f"REPORTE DE CAJA - MES {mes}/{anio}")
    print(f"{'ID':<4} | {'Fecha':<10} | {'Cliente':<12} | {'Pago':<12} | {'Valor':<8} | {'Ayudante':<10} | {'Pago Ay.'}")
    print(f"{'-'*90}")

    for s in servicios:
        if s['mes'] == mes and s['anio'] == anio:
            if s['metodo_pago'] == "Efectivo": efectivo += s['valor']
            else: mercado_pago += s['valor']
            
            total_propinas += s['propina']
            pago_empleados += s['pago_ayudante']
            
            print(f"{s['id']:<4} | {s['fecha']:<10} | {s['cliente']:<12} | {s['metodo_pago']:<12} | ${s['valor']:<7} | {s['ayudante']:<10} | ${s['pago_ayudante']}")

    total_bruto = efectivo + mercado_pago
    print(f"{'='*90}")
    print(f"💵 Efectivo en Caja:      ${efectivo}")
    print(f"📱 Mercado Pago:          ${mercado_pago}")
    print(f"💰 Propina total del mes: ${total_propinas}")
    print(f"👷 Pago a Ayudantes:      -${pago_empleados}")
    print(f"{'-'*30}")
    print(f"📊 GANANCIA TOTAL (Sin contar empleados): ${total_bruto + total_propinas}")
    print(f"🚀 GANANCIA NETA (Lo que te queda):      ${(total_bruto + total_propinas) - pago_empleados}")

def menu():
    while True:
        print("\n--- SISTEMA LAVADERO PRO ---")
        print("1. Registrar Cliente\n2. Cargar Lavado\n3. Eliminar Lavado\n4. Reporte Mensual\n5. Salir")
        op = input("Opción: ")
        if op == "1": registrar_cliente()
        elif op == "2": cargar_lavado()
        elif op == "3": eliminar_lavado()
        elif op == "4": mostrar_reporte()
        elif op == "5": break

if __name__ == "__main__":
    menu()