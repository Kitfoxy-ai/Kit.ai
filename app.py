import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
import base64
import json
import os

# --- CONFIGURACIÓN DE KIT ---
NOMBRE_IA = "Kit"
SISTEMA = f"Eres {NOMBRE_IA}, el colega tecnológico del usuario. Informal y directo. Llama al usuario 'Jefe'."
MI_LLAVE = "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".strip()
ARCHIVO_CHATS = "historial_chats.json"

st.set_page_config(page_title=NOMBRE_IA, page_icon="⚡")
client = Groq(api_key=MI_LLAVE)

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_chats():
    if os.path.exists(ARCHIVO_CHATS):
        try:
            with open(ARCHIVO_CHATS, "r") as f:
                return json.load(f)
        except:
            return {"Chat 1": [{"role": "system", "content": SISTEMA}]}
    return {"Chat 1": [{"role": "system", "content": SISTEMA}]}

def guardar_chats(chats):
    with open(ARCHIVO_CHATS, "w") as f:
        json.dump(chats, f)

# Inicializar sesión
if "todos_los_chats" not in st.session_state:
    st.session_state.todos_los_chats = cargar_chats()
if "chat_actual" not in st.session_state:
    st.session_state.chat_actual = list(st.session_state.todos_los_chats.keys())[0]

# --- BARRA LATERAL (GESTIÓN DE CHATS) ---
st.sidebar.title("🗂️ Mis Conversaciones")

if st.sidebar.button("➕ Nuevo Chat"):
    nuevo_id = f"Chat {len(st.session_state.todos_los_chats) + 1}"
    st.session_state.todos_los_chats[nuevo_id] = [{"role": "system", "content": SISTEMA}]
    st.session_state.chat_actual = nuevo_id
    guardar_chats(st.session_state.todos_los_chats)
    st.rerun()

st.session_state.chat_actual = st.sidebar.selectbox(
    "Seleccionar conversación:", 
    list(st.session_state.todos_los_chats.keys()),
    index=list(st.session_state.todos_los_chats.keys()).index(st.session_state.chat_actual)
)

if st.sidebar.button("🗑️ Borrar este Chat"):
    if len(st.session_state.todos_los_chats) > 1:
        del st.session_state.todos_los_chats[st.session_state.chat_actual]
        st.session_state.chat_actual = list(st.session_state.todos_los_chats.keys())[0]
    else:
        st.session_state.todos_los_chats["Chat 1"] = [{"role": "system", "content": SISTEMA}]
    guardar_chats(st.session_state.todos_los_chats)
    st.rerun()

# --- INTERFAZ PRINCIPAL CON PESTAÑAS ---
st.title(f"⚡ {st.session_state.chat_actual}")
tab_chat, tab_vision = st.tabs(["💬 Chat", "📸 Visión"])

# --- PESTAÑA DE VISIÓN ---
with tab_vision:
    st.subheader("Ojos de Kit")
    foto = st.camera_input("Capturar entorno")
    if foto:
        with st.spinner("Kit analizando..."):
            try:
                bytes_data = foto.getvalue()
                base64_image = base64.b64encode(bytes_data).decode('utf-8')
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Jefe, analiza esto rápido."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                respuesta = res.choices[0].message.content
                st.session_state.todos_los_chats[st.session_state.chat_actual].append({"role": "assistant", "content": f"[Análisis de Imagen]: {respuesta}"})
                guardar_chats(st.session_state.todos_los_chats)
                
                limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
                components.html(f'<script>window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance("{limpio}"); m.lang="es-ES"; m.pitch=0.75; window.speechSynthesis.speak(m);</script>', height=0)
                st.success("Imagen analizada. Mira el historial en la pestaña Chat.")
            except Exception as e:
                st.error(f"Error de visión: {e}")

# --- PESTAÑA DE CHAT ---
with tab_chat:
    mensajes_actuales = st.session_state.todos_los_chats[st.session_state.chat_actual]
    for message in mensajes_actuales:
        if message["role"] != "system":
            with st.chat_message(message["role"], avatar="⚡" if message["role"]=="assistant" else None):
                st.markdown(message["content"])

    # Entrada de texto
    prompt = st.chat_input("Escribe algo, Jefe...")
    if prompt:
        st.session_state.todos_los_chats[st.session_state.chat_actual].append({"role": "user", "content": prompt})
        guardar_chats(st.session_state.todos_los_chats)
        st.rerun()

    # Respuesta automática si el último es del usuario
    if mensajes_actuales[-1]["role"] == "user":
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=mensajes_actuales)
            respuesta = res.choices[0].message.content
            st.session_state.todos_los_chats[st.session_state.chat_actual].append({"role": "assistant", "content": respuesta})
            guardar_chats(st.session_state.todos_los_chats)
            
            limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
            components.html(f'<script>window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance("{limpio}"); m.lang="es-ES"; m.pitch=0.75; window.speechSynthesis.speak(m);</script>', height=0)
            st.rerun()
        except Exception as e:
            st.error(f"Fallo en el procesador: {e}")
