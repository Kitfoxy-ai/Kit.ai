import streamlit as st
from groq import Groq
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE KIT ---
NOMBRE_IA = "Kit"
SISTEMA = f"Eres {NOMBRE_IA}, el colega tecnológico del usuario. Háblale de tú, sé informal, directo y usa un toque de sarcasmo. Llama al usuario 'Jefe'. No seas un robot aburrido."

# Tu API KEY integrada
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
        # Petición a Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=st.session_state.messages
        )
        
        # --- CORRECCIÓN AQUÍ: Acceso correcto al mensaje ---
        respuesta = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(respuesta)

        # VOZ AUTOMÁTICA
                # VOZ AUTOMÁTICA FORZADA (MASculino)
        limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
        js_kit = f"""
            <script>
            function hablar() {{
                var msg = new SpeechSynthesisUtterance("{limpio}");
                var voices = window.speechSynthesis.getVoices();

                // Filtro para buscar una voz que NO sea femenina
                var vozMasculina = voices.find(v => 
                    (v.name.toLowerCase().includes('male') || 
                     v.name.toLowerCase().includes('masculino') || 
                     v.name.toLowerCase().includes('jorge') || 
                     v.name.toLowerCase().includes('juan') || 
                     v.name.toLowerCase().includes('espanya')) && 
                    v.lang.includes('es')
                );

                if (vozMasculina) {{
                    msg.voice = vozMasculina;
                }}

                msg.pitch = 0.8;  // Baja el tono para que suene más grave/masculino
                msg.rate = 1.0;   // Velocidad normal
                window.speechSynthesis.speak(msg);
            }}

            // Las voces tardan en cargar, este truco ayuda a que el código las encuentre
            if (window.speechSynthesis.onvoiceschanged !== undefined) {{
                window.speechSynthesis.onvoiceschanged = hablar;
            }}
            hablar();
            </script>
        """
        components.html(js_kit, height=0)
            
