import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
import base64

# --- CONFIGURACIÓN DE KIT ---
NOMBRE_IA = "Kit"
SISTEMA = f"Eres {NOMBRE_IA}, el colega tecnológico del usuario. Tienes visión. Analiza las fotos de forma informal y directa. Llama al usuario 'Jefe'."
MI_LLAVE = "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".strip()

st.set_page_config(page_title=NOMBRE_IA, page_icon="⚡", layout="centered")
st.title(f"⚡ {NOMBRE_IA} Vision OS")

client = Groq(api_key=MI_LLAVE)

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SISTEMA}]

# --- BARRA LATERAL ---
st.sidebar.title("🛠️ Panel de Control")
vision_activa = st.sidebar.toggle("Activar Sensores Visuales", value=False)

if st.sidebar.button("🗑️ Borrar Memoria (Historial)"):
    st.session_state.messages = [{"role": "system", "content": SISTEMA}]
    st.rerun()

# --- MODO VISIÓN (CÁMARA TRASERA) ---
if vision_activa:
    # 'facing_mode="environment"' es lo que obliga al móvil a usar la cámara trasera
    foto = st.camera_input("📸 Escaneando entorno...", facing_mode="environment")
    
    if foto:
        with st.spinner("Kit analizando..."):
            try:
                bytes_data = foto.getvalue()
                base64_image = base64.b64encode(bytes_data).decode('utf-8')
                
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Jefe, ya estoy mirando por la cámara trasera. ¿Qué me cuentas de esto?"},
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

# --- HISTORIAL VISUAL ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="⚡" if message["role"]=="assistant" else None):
            st.markdown(message["content"])

# --- CHAT DE TEXTO ---
prompt = st.chat_input("Dime algo, Jefe...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Respuesta de texto si el último es del usuario
if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "user":
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=st.session_state.messages
        )
        respuesta = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        # Audio para texto
        limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
        js_txt = f"""<script>window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance("{limpio}"); m.lang='es-ES'; m.pitch=0.75; window.speechSynthesis.speak(m);</script>"""
        components.html(js_txt, height=0)
        st.rerun()
    except Exception as e:
        st.error(f"Fallo en el procesador: {e}")
                
