import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
import base64

# --- CONFIGURACIÓN DE KIT CON VISIÓN ---
NOMBRE_IA = "Kit"
SISTEMA = f"Eres {NOMBRE_IA}, el colega tecnológico del usuario. Tienes visión. Si te pasan una foto, analízala de forma informal y directa. Llama al usuario 'Jefe'."
MI_LLAVE = "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".strip()

st.set_page_config(page_title=NOMBRE_IA, page_icon="⚡")
st.title(f"⚡ {NOMBRE_IA} Vision OS")

client = Groq(api_key=MI_LLAVE)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SISTEMA}]

# --- INTERFAZ DE CÁMARA ---
foto = st.camera_input("📸 Cámara de Kit")

def procesar_foto(imagen):
    # Convertir imagen a formato que entienda la IA
    bytes_data = imagen.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')
    
    return client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Jefe, ¿qué quieres que mire en esta foto?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    )

if foto:
    with st.spinner("Kit está mirando..."):
        try:
            res = procesar_foto(foto)
            respuesta = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            st.chat_message("assistant", avatar="⚡").write(respuesta)

            # VOZ AUTOMÁTICA
            limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
            js_kit = f"""
                <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{limpio}");
                msg.lang = 'es-ES';
                msg.pitch = 0.75; 
                msg.rate = 1.0;  
                window.speechSynthesis.speak(msg);
                </script>
            """
            components.html(js_kit, height=0)
        except Exception as e:
            st.error(f"Error de visión: {e}")

# Entrada de texto normal
prompt = st.chat_input("Dime algo, Jefe...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=st.session_state.messages)
    respuesta = res.choices[0].message.content
    st.chat_message("assistant", avatar="⚡").write(respuesta)
            
