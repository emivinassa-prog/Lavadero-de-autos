import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- CONEXIÓN A GOOGLE SHEETS ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Abrir la hoja (Asegúrate de que el nombre coincida con tu archivo de Google Sheets)
try:
    sheet = client.open("DatosLavadero").sheet1
except:
    st.error("No se encontró la hoja 'DatosLavadero'. Revisa el nombre y que esté compartida.")

# Función para cargar datos desde Sheets
def cargar_datos():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# --- INTERFAZ ---
st.set_page_config(page_title="Lavadero Magic Detail", layout="centered")
st.sidebar.title("🧼 Menú")
menu = st.sidebar.radio("Ir a:", ["Cargar Lavado", "Reporte"])

if menu == "Cargar Lavado":
    st.header("🚿 Nuevo Lavado")
    with st.form("lavado_form", clear_on_submit=True):
        cliente = st.text_input("Cliente")
        vehiculo = st.text_input("Vehículo")
        monto = st.number_input("Precio $", min_value=0)
        metodo = st.selectbox("Pago", ["Efectivo", "Mercado Pago"])
        
        if st.form_submit_button("Guardar"):
            nueva_fila = [datetime.now().strftime("%d/%m/%Y"), cliente, vehiculo, monto, metodo]
            sheet.append_row(nueva_fila)
            st.success("✅ Guardado en Google Sheets")

elif menu == "Reporte":
    st.header("📊 Registros")
    df = cargar_datos()
    if not df.empty:
        st.dataframe(df)
        st.metric("Total Recaudado", f"${df['Precio $'].sum()}")
    else:
        st.write("Aún no hay datos.")
