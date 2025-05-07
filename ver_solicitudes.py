import streamlit as st
import requests

API_URL = "http://localhost:5001/solicitudes"
USUARIOS_URL = "http://localhost:5001/usuarios"

st.set_page_config(page_title="Solicitudes Recibidas", layout="centered")
st.title("📋 Solicitudes Recibidas - Área de Sistemas")

try:
    response = requests.get(API_URL)
    response.raise_for_status()
    solicitudes = response.json()

    response_usuarios = requests.get(USUARIOS_URL)
    response_usuarios.raise_for_status()
    usuarios = response_usuarios.json()
    usuarios_dict = {u["documento"]: u["nombre"] for u in usuarios}

    if not solicitudes:
        st.info("No hay solicitudes registradas.")
    else:
        filtro_doc = st.text_input("🔎 Filtrar por documento (opcional):")
        filtro_estado = st.selectbox("🟡 Filtrar por estado", ["Todos", "P", "R", "C"], index=0)

        if filtro_doc:
            solicitudes = [s for s in solicitudes if filtro_doc in s["documento"]]
        if filtro_estado != "Todos":
            solicitudes = [s for s in solicitudes if s["estado"] == filtro_estado]

        for s in solicitudes:
            nombre = s.get("nombre") or usuarios_dict.get(s["documento"], "Sin nombre")

            with st.expander(f"🔢 Solicitud #{s['consecutivo']} — {nombre}"):
                st.markdown(f"""
                📅 **Fecha:** `{s['fecha']}` — 🕒 **Hora:** `{s['hora']}`  
                🆔 **Documento:** `{s['documento']}`  
                📝 **Asunto:** {s['asunto']}  
                📄 **Descripción:** {s['descripcion']}  
                🟡 **Estado actual:** `{s['estado']}`
                """)

                nuevo_estado = st.selectbox(
                    f"🔧 Cambiar estado de la solicitud #{s['consecutivo']}",
                    ["P", "R", "C","A","F","X","S"],
                    index=["P", "R", "C","A","F","X","S"].index(s["estado"]),
                    key=f"estado_{s['consecutivo']}"
                )

                if st.button(f"💾 Guardar cambios #{s['consecutivo']}"):
                    payload = {
                        "estado": nuevo_estado,
                        "usuario": "sistemas"  # Aquí podrías reemplazar con un login si quieres
                    }
                    try:
                        update_url = f"{API_URL}/{s['consecutivo']}"
                        r = requests.put(update_url, json=payload)
                        r.raise_for_status()
                        st.success(f"✅ Estado actualizado para solicitud #{s['consecutivo']}.")
                    except Exception as e:
                        st.error("❌ Error al actualizar estado.")
                        st.text(str(e))

except Exception as e:
    st.error("Error al obtener las solicitudes.")
    st.text(str(e))