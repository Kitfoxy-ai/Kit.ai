import streamlit as st
from groq import Groq
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE KIT ---
NOMBRE_IA = "Kit"
SISTEMA = f"Eres {NOMBRE_IA}, el colega tecnológico del usuario. Háblale de tú, sé informal, directo y usa un toque de sarcasmo. Llama al usuario 'Jefe'. No seas un robot aburrido."

# Tu API KEY (limpiamos posibles espacios invisibles)
MI_LLAVE = "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".strip()

st.set_page_config(page_title=NOMBRE_IA, page_icon="⚡")
st.title(f"⚡ {NOMBRE_IA} Online")

# Conectamos con el cerebro de Kit
try:
    client = Groq(api_key=MI_LLAVE)
except Exception as e:
    st.error(f"Error al conectar con el cerebro: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SISTEMA}]

# Historial de chat visual
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Entrada de voz/texto
prompt = st.chat_input("Dime algo, Jefe...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Probamos con un modelo muy estable: llama-3.1-8b-instant
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=st.session_state.messages
        )
        
        respuesta = completion.choices.message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(respuesta)

        # VOZ AUTOMÁTICA
        js_kit = f"""
            <script>
            var msg = new SpeechSynthesisUtterance("{respuesta.replace('"', '').replace('\\n', ' ')}");
            msg.lang = 'es-ES';
            msg.pitch = 1.0; 
            msg.rate = 1.1;  
            window.speechSynthesis.speak(msg);
            </script>
        """
        components.html(js_kit, height=0)
    except Exception as e:
        st.error(f"Oye Jefe, algo ha fallado con Groq: {e}")
                                     
