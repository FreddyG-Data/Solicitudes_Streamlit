import streamlit as st
import requests

st.set_page_config(page_title="Solicitudes Recibidas", layout="centered")
st.title("📋 Solicitudes Recibidas - Área de Sistemas")

API_URL = "http://localhost:5001/solicitudes"  # Asegúrate de que Flask esté corriendo

# Obtener solicitudes desde la API
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    solicitudes = response.json()

    if not solicitudes:
        st.info("No hay solicitudes registradas.")
    else:
        # Agregar opción de búsqueda y filtros básicos (opcional)
        filtro_doc = st.text_input("🔎 Filtrar por documento (opcional):")
        filtro_estado = st.selectbox("🟡 Filtrar por estado", ["Todos", "P", "R", "C"], index=0)

        # Aplicar filtros
        if filtro_doc:
            solicitudes = [s for s in solicitudes if filtro_doc in s["documento"]]
        if filtro_estado != "Todos":
            solicitudes = [s for s in solicitudes if s["estado"] == filtro_estado]

        # Mostrar solicitudes
        for s in solicitudes:
            st.markdown(f"""
            ---
            🔢 **Solicitud #{s['consecutivo']}**  
            📅 Fecha: `{s['fecha']}` — 🕒 Hora: `{s['hora']}`  
            🆔 Documento: `{s['documento']}`  
            📝 **Asunto:** {s['asunto']}  
            📄 **Descripción:** {s['descripcion']}  
            🟡 **Estado:** `{s['estado']}`
            """)
except Exception as e:
    st.error("Error al obtener las solicitudes.")
    st.text(str(e))
