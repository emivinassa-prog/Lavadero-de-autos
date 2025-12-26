import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# --- CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="Lavadero Pro App", layout="centered")

ARCHIVO_DB = "base_datos_lavadero.json"

def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, "r") as f:
            return json.load(f)
    return {"clientes": {}, "servicios": [], "contador": 1}

def guardar_datos(data):
    with open(ARCHIVO_DB, "w") as f:
        json.dump(data, f, indent=4)

# Inicializar la base de datos en la sesión
if 'db' not in st.session_state:
    st.session_state.db = cargar_datos()

db = st.session_state.db

# --- MENÚ LATERAL ---
st.sidebar.header("🧼 Menú Principal")
opcion = st.sidebar.radio("Seleccione una acción:", 
                         ["Cargar Lavado", "Registrar Cliente", "Reporte Mensual", "Eliminar Registro"])

# --- 1. REGISTRAR CLIENTE ---
if opcion == "Registrar Cliente":
    st.header("👤 Registrar Nuevo Cliente")
    with st.form("form_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre del Cliente")
        telefono = st.text_input("Teléfono (completo)")
        vehiculos_raw = st.text_input("Vehículos (si es más de uno, separar con coma)")
        
        if st.form_submit_button("Guardar Cliente"):
            if nombre and telefono:
                id_busqueda = telefono[-4:]
                db["clientes"][id_busqueda] = {
                    "nombre": nombre,
                    "telefono": telefono,
                    "vehiculos": [v.strip() for v in vehiculos_raw.split(",")]
                }
                guardar_datos(db)
                st.success(f"✅ Cliente {nombre} guardado (ID: {id_busqueda})")
            else:
                st.error("Por favor completa nombre y teléfono.")

# --- 2. CARGAR LAVADO ---
elif opcion == "Cargar Lavado":
    st.header("🚿 Cargar Lavado")
    busqueda = st.text_input("Ingrese los últimos 4 dígitos del teléfono")
    
    if busqueda in db["clientes"]:
        cliente = db["clientes"][busqueda]
        st.info(f"Cliente seleccionado: **{cliente['nombre']}**")
        
        with st.form("form_lavado", clear_on_submit=True):
            vehi_sel = st.selectbox("Seleccione Vehículo", cliente["vehiculos"])
            tipo_lavado = st.selectbox("Tipo de Lavado", 
                                      ["Lavado básico", "Lavado a domicilio", "Limpieza de motor", 
                                       "Ópticas", "Abrillantado", "Limpieza de tapizado"])
            metodo_pago = st.radio("Método de Pago", ["Efectivo", "Mercado Pago"], horizontal=True)
            valor = st.number_input("Valor del Servicio $", min_value=0)
            propina = st.number_input("Propina $", min_value=0)
            
            ayu = st.selectbox("Ayudante", ["No hubo", "Vicki", "Maxi", "Soto"])
            pago_ayu = st.number_input(f"¿Cuánto se le pagó a {ayu}?", min_value=0) if ayu != "No hubo" else 0
            
            if st.form_submit_button("Registrar Lavado"):
                nuevo_lavado = {
                    "id": db["contador"],
                    "fecha": datetime.now().strftime("%d/%m/%Y"),
                    "mes": datetime.now().month,
                    "anio": datetime.now().year,
                    "cliente": cliente["nombre"],
                    "vehiculo": vehi_sel,
                    "tipo": tipo_lavado,
                    "metodo": metodo_pago,
                    "valor": valor,
                    "propina": propina,
                    "ayudante": ayu,
                    "pago_ayu": pago_ayu
                }
                db["servicios"].append(nuevo_lavado)
                db["contador"] += 1
                guardar_datos(db)
                st.success(f"✨ Lavado ID {nuevo_lavado['id']} guardado correctamente.")
    elif busqueda:
        st.warning("⚠️ Cliente no encontrado. Regístrelo primero.")

# --- 3. REPORTE MENSUAL ---
elif opcion == "Reporte Mensual":
    st.header("📊 Reporte de Ganancias")
    mes_sel = st.selectbox("Seleccione el Mes", range(1, 13), index=datetime.now().month - 1)
    
    if db["servicios"]:
        df = pd.DataFrame(db["servicios"])
        df_mes = df[(df["mes"] == mes_sel) & (df["anio"] == datetime.now().year)]
        
        if not df_mes.empty:
            st.dataframe(df_mes[["id", "fecha", "cliente", "vehiculo", "metodo", "valor", "ayudante", "pago_ayu"]])
            
            # Cálculos rápidos
            efectivo = df_mes[df_mes["metodo"] == "Efectivo"]["valor"].sum()
            mp = df_mes[df_mes["metodo"] == "Mercado Pago"]["valor"].sum()
            total_propinas = df_mes["propina"].sum()
            total_ayudantes = df_mes["pago_ayu"].sum()
            
            total_bruto = efectivo + mp + total_propinas # Ganancia total con propina
            neta = total_bruto - total_ayudantes # Ganancia final sin empleados
            
            c1, c2 = st.columns(2)
            c1.metric("Efectivo", f"${efectivo}")
            c1.metric("Mercado Pago", f"${mp}")
            c2.metric("Total Propinas", f"${total_propinas}")
            c2.metric("Pago Ayudantes", f"-${total_ayudantes}")
            
            st.divider()
            st.subheader(f"🚀 GANANCIA NETA TOTAL: ${neta}")
        else:
            st.write("No hay registros para este mes.")
    else:
        st.write("Aún no hay datos cargados.")

# --- 4. ELIMINAR ---
elif opcion == "Eliminar Registro":
    st.header("🗑️ Eliminar Lavado")
    id_borrar = st.number_input("Ingrese el ID del lavado a borrar", min_value=1)
    if st.button("Eliminar permanentemente"):
        db["servicios"] = [s for s in db["servicios"] if s["id"] != id_borrar]
        guardar_datos(db)
        st.error(f"Registro {id_borrar} eliminado.")
