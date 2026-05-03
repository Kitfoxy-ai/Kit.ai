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
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=st.session_state.messages
        )
        
        respuesta = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(respuesta)

        # --- VOZ MASCULINA FORZADA ---
        limpio = respuesta.replace('"', '').replace('\n', ' ').replace("'", "")
        js_kit = f"""
            <script>
            function hablar() {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{limpio}");
                var voices = window.speechSynthesis.getVoices();

                // Intentamos encontrar una voz que sea explícitamente masculina o de hombre
                var vozMasculina = voices.find(v => 
                    (v.name.toLowerCase().includes('jorge') || 
                     v.name.toLowerCase().includes('juan') || 
                     v.name.toLowerCase().includes('david') || 
                     v.name.toLowerCase().includes('paul') || 
                     v.name.toLowerCase().includes('male')) && 
                    v.lang.includes('es')
                );

                // Si no encuentra ninguna por nombre, filtramos las que NO queremos (mujeres)
                if (!vozMasculina) {{
                    vozMasculina = voices.find(v => 
                        v.lang.includes('es') && 
                        !v.name.toLowerCase().includes('helena') && 
                        !v.name.toLowerCase().includes('laura') && 
                        !v.name.toLowerCase().includes('google')
                    );
                }}

                if (vozMasculina) {{
                    msg.voice = vozMasculina;
                }}

                msg.pitch = 0.7; // Muy grave para forzar masculinidad
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
            }}

            if (window.speechSynthesis.getVoices().length === 0) {{
                window.speechSynthesis.onvoiceschanged = hablar;
            }} else {{
                hablar();
            }}
            </script>
        """
        components.html(js_kit, height=0)

    except Exception as e:
        st.error(f"Oye Jefe, algo ha fallado con Groq: {e}")
