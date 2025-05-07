import streamlit as st
import requests

API_URL = "http://localhost:5001/solicitudes"
USUARIOS_URL = "http://localhost:5001/usuarios"

st.title("🛠️ Solicitud de Soporte Técnico")

# 1. Obtener lista de usuarios desde la API
try:
    response = requests.get(USUARIOS_URL)
    response.raise_for_status()
    usuarios = response.json()

    # Crear lista de nombres de usuarios
    nombres = [u["nombre"] for u in usuarios]
    seleccion = st.selectbox("👤 Selecciona tu nombre", nombres)

    # Buscar el usuario seleccionado
    usuario = next((u for u in usuarios if u["nombre"] == seleccion), None)

    # Mostrar campo para documento si no está en la base (verificando documento)
    if usuario and usuario.get("documento"):
        # Si tiene documento, lo usamos directamente (no se muestra)
        doc_usuario = usuario["documento"]
        st.markdown(f"🆔 Tu cédula está registrada.")
    else:
        # Si no tiene documento, pedirlo
        doc_usuario = st.text_input("🔢 Ingresa tu número de cédula")
        
except Exception as e:
    st.error("No se pudo cargar la lista de usuarios.")
    st.stop()

# 2. Formulario de solicitud
asunto = st.text_input("📝 Asunto")
descripcion = st.text_area("📄 Descripción del problema")

# 3. Enviar solicitud
if st.button("📨 Enviar solicitud"):
    if not doc_usuario:
        st.warning("Debes ingresar tu número de cédula para enviar la solicitud.")
    elif not asunto or not descripcion:
        st.warning("Todos los campos son obligatorios.")
    else:
        payload = {
            "documento": doc_usuario,
            "asunto": asunto,
            "descripcion": descripcion
        }
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            st.success("✅ Solicitud enviada correctamente.")
        except Exception as e:
            st.error("❌ Error al enviar la solicitud.")
            st.text(str(e))