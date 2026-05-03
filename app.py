import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
import base64

# --- CONFIGURACIÓN DE KIT ---
NOMBRE_IA = "Kit"
SISTEMA = f"Eres {NOMBRE_IA}, el colega tecnológico del usuario. Háblale de tú, sé informal y directo. Llama al usuario 'Jefe'."
MI_LLAVE = "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".strip()

st.set_page_config(page_title=NOMBRE_IA, page_icon="⚡")
st.title(f"⚡ {NOMBRE_IA} Vision OS")

client = Groq(api_key=MI_LLAVE)

# Inicializar el historial si no existe
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SISTEMA}]

# --- INTERRUPTOR DE CÁMARA ---
st.sidebar.title("Configuración")
vision_activa = st.sidebar.toggle("Activar Sensores Visuales", value=False)

if vision_activa:
    foto = st.camera_input("📸 Ojos de Kit")
    
    if foto:
        with st.spinner("Kit analizando..."):
            try:
                # Procesar imagen
                bytes_data = foto.getvalue()
                base64_image = base64.b64encode(bytes_data).decode('utf-8')
                
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Jefe, ya estoy mirando. ¿Qué ves de especial aquí?"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }]
                )
                respuesta = res.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
            except Exception as e:
                st.error(f"Error de visión: {e}")

# --- MOSTRAR HISTORIAL COMPLETO ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="⚡" if message["role"]=="assistant" else None):
            st.markdown(message["content"])

# --- CHAT DE TEXTO ---
prompt = st.chat_input("Dime algo, Jefe...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Forzar refresco para mostrar el mensaje del usuario inmediatamente
    st.rerun()

# Si el último mensaje es del usuario, generar respuesta de Kit
if st.session_state.messages[-1]["role"] == "user":
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=st.session_state.messages
        )
        respuesta = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        # Audio automático para la última respuesta
        limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
        js_texto = f"""
            <script>
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{limpio}");
            msg.lang = 'es-ES';
            msg.pitch = 0.75; 
            msg.rate = 1.0;  
            window.speechSynthesis.speak(msg);
            </script>
        """
        components.html(js_texto, height=0)
        st.rerun()
    except Exception as e:
        st.error(f"Fallo en el procesador: {e}")
        
