import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
import base64

# --- CONFIGURACIÓN DE KIT ---
NOMBRE_IA = "Kit"
SISTEMA = f"Eres {NOMBRE_IA}, el colega tecnológico del usuario. Tienes visión. Analiza las fotos de forma informal y directa. Llama al usuario 'Jefe'."
MI_LLAVE = "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".strip()

st.set_page_config(page_title=NOMBRE_IA, page_icon="⚡")
st.title(f"⚡ {NOMBRE_IA} Vision OS")

client = Groq(api_key=MI_LLAVE)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SISTEMA}]

# --- PANEL DE CONTROL LATERAL ---
st.sidebar.title("🛠️ Sensores de Kit")
opcion_camara = st.sidebar.radio(
    "Selecciona Cámara:",
    ("Apagada", "Cámara Frontal (Selfie)", "Cámara Trasera (Mundo)"),
    index=0
)

if st.sidebar.button("🗑️ Borrar Memoria"):
    st.session_state.messages = [{"role": "system", "content": SISTEMA}]
    st.rerun()

# --- LÓGICA DE VISIÓN ---
if opcion_camara != "Apagada":
    # Configurar el modo según la elección
    modo = "user" if opcion_camara == "Cámara Frontal (Selfie)" else "environment"
    
    foto = st.camera_input(f"📸 {opcion_camara} activa", facing_mode=modo)
    
    if foto:
        with st.spinner("Kit procesando imagen..."):
            try:
                bytes_data = foto.getvalue()
                base64_image = base64.b64encode(bytes_data).decode('utf-8')
                
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Jefe, ya veo. ¿Qué quieres que analice de lo que tengo delante?"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }]
                )
                respuesta = res.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
                
                # Audio para visión
                limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
                js_vis = f"""<script>window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance("{limpio}"); m.lang='es-ES'; m.pitch=0.75; window.speechSynthesis.speak(m);</script>"""
                components.html(js_vis, height=0)
            except Exception as e:
                st.error(f"Error de visión: {e}")

# --- HISTORIAL Y CHAT ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="⚡" if message["role"]=="assistant" else None):
            st.markdown(message["content"])

prompt = st.chat_input("Dime algo, Jefe...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "user":
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=st.session_state.messages)
        respuesta = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
        js_txt = f"""<script>window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance("{limpio}"); m.lang='es-ES'; m.pitch=0.75; window.speechSynthesis.speak(m);</script>"""
        components.html(js_txt, height=0)
        st.rerun()
    except Exception as e:
        st.error(f"Fallo en el procesador: {e}")
                
