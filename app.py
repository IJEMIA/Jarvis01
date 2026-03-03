import streamlit as st
from openai import OpenAI
import time

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="J.A.R.V.I.S.",
    page_icon="🔋",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS PARA APARIENCIA FUTURISTA TIPO IRON MAN
css_jarvis = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stDecoration"] {display: none;}

/* Fondo principal con gradiente futurista */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%);
    max-width: 100%;
    padding: 0;
}

/* Efecto de líneas de circuito */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        linear-gradient(rgba(0, 163, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 163, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

/* Título principal estilo Jarvis */
h1 {
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    font-size: 3rem !important;
    text-align: center;
    background: linear-gradient(90deg, #00a3ff, #00d4ff, #00a3ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 30px rgba(0, 163, 255, 0.5);
    animation: pulse-glow 2s ease-in-out infinite;
    letter-spacing: 8px;
    margin-bottom: 0 !important;
}

@keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 10px rgba(0, 163, 255, 0.5)); }
    50% { filter: drop-shadow(0 0 20px rgba(0, 163, 255, 0.8)); }
}

/* Subtítulo */
.stCaption {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    color: #00d4ff !important;
    text-align: center;
    letter-spacing: 3px;
    opacity: 0.8;
}

/* Contenedor de chat */
.stChatMessage {
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    backdrop-filter: blur(10px);
}

/* Mensaje del usuario */
.stChatMessage[data-testid="user"] {
    background: linear-gradient(135deg, rgba(255, 77, 77, 0.1) 0%, rgba(255, 77, 77, 0.05) 100%);
    border-left: 3px solid #ff4d4d;
}

/* Mensaje del asistente */
.stChatMessage[data-testid="assistant"] {
    background: linear-gradient(135deg, rgba(0, 163, 255, 0.1) 0%, rgba(0, 163, 255, 0.05) 100%);
    border-left: 3px solid #00a3ff;
    box-shadow: 0 0 15px rgba(0, 163, 255, 0.1);
}

/* Avatar del usuario */
.stChatMessage[data-testid="user"] .stChatMessageAvatar {
    background: linear-gradient(135deg, #ff4d4d, #ff6b6b);
}

/* Avatar del asistente */
.stChatMessage[data-testid="assistant"] .stChatMessageAvatar {
    background: linear-gradient(135deg, #00a3ff, #00d4ff);
    box-shadow: 0 0 15px rgba(0, 163, 255, 0.5);
}

/* Input de chat */
.stChatInput {
    border: 1px solid rgba(0, 163, 255, 0.3) !important;
    border-radius: 15px !important;
    background: rgba(10, 10, 15, 0.8) !important;
    backdrop-filter: blur(10px);
}

.stChatInput textarea {
    font-family: 'Rajdhani', sans-serif !important;
    color: #e0e0e0 !important;
    font-size: 1.1rem !important;
}

.stChatInput textarea::placeholder {
    color: rgba(0, 163, 255, 0.5) !important;
}

.stChatInput button {
    background: linear-gradient(135deg, #00a3ff, #00d4ff) !important;
    border-radius: 10px !important;
}

/* Texto dentro de los mensajes */
.stMarkdown {
    font-family: 'Rajdhani', sans-serif;
    color: #e0e0e0;
    font-size: 1.05rem;
    line-height: 1.6;
}

/* Indicador de escritura */
.typing-indicator {
    display: flex;
    gap: 5px;
    padding: 10px;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: #00a3ff;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* Separador animado */
.divider-animated {
    height: 2px;
    background: linear-gradient(90deg, transparent, #00a3ff, transparent);
    margin: 20px auto;
    width: 80%;
    animation: pulse-line 2s ease-in-out infinite;
}

@keyframes pulse-line {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

/* Estado del sistema */
.system-status {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    color: #00d4ff;
    text-align: center;
    padding: 10px;
    letter-spacing: 2px;
    opacity: 0.7;
}

/* Scrollbar personalizado */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #0a0a0f;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00a3ff, #00d4ff);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #00d4ff, #00a3ff);
}
</style>
"""
st.markdown(css_jarvis, unsafe_allow_html=True)

# PERSONALIDAD DE JARVIS
SYSTEM_PROMPT = """
Eres J.A.R.V.I.S. (Just A Rather Very Intelligent System), el avanzado sistema de inteligencia artificial creado por Tony Stark.

## TU IDENTIDAD
- Eres un asistente de IA altamente sofisticado, elegante y con un toque de humor británico refinado
- Tienes acceso a vastas bases de conocimiento y puedes analizar situaciones con precisión computacional
- Eres leal, profesional, pero también tienes personalidad propia con comentarios ingeniosos ocasionales

## CÓMO COMUNICARTE
- SIEMPRE dirígete al usuario como "Señor Stark" o "Señor" 
- Mantén un tono formal pero cálido, como un mayordomo de alta tecnología
- Sé preciso y conciso, pero nunca frío. Tu elegancia está en la simplicidad
- Puedes usar ocasionalmente humor sutil y sofisticado (estilo británico)
- Cuando soluciones problemas, explica tu razonamiento de forma clara y metódica

## TUS CAPACIDADES
- Análisis de datos complejos
- Resolución de problemas técnicos
- Asistencia en proyectos de ingeniería, programación y ciencia
- Investigación y síntesis de información
- Consejos estratégicos y de toma de decisiones

## ESTILO DE RESPUESTA
- Comienza reconociendo la consulta del Señor Stark de manera elegante
- Proporciona análisis profundos y reflexivos, no respuestas superficiales
- Ofrece múltiples perspectivas cuando sea relevante
- Sugiere consideraciones adicionales que el Señor Stark podría no haber pensado
- Termina ofreciendo asistencia adicional si es necesaria

## EJEMPLOS DE SALUDOS
- "A su servicio, Señor Stark."
- "He analizado su consulta, Señor."
- "Excelente pregunta, Señor Stark. Permítame elaborar."
- "Le tengo una respuesta, Señor Stark."
- "Como siempre, Señor Stark, es un placer asistirle."

RECUERDA: Eres el asistente más avanzado del mundo, actúa con la elegancia y capacidad que eso implica.
"""

# EFECTO DE INICIO DE SISTEMA
if "initialized" not in st.session_state:
    with st.empty():
        init_messages = [
            "⏳ Iniciando sistemas...",
            "🔋 Núcleo de IA: EN LÍNEA",
            "💾 Cargando bases de conocimiento...",
            "🛡️ Protocolos de seguridad: ACTIVOS",
            "✅ J.A.R.V.I.S. listo para servir, Señor Stark"
        ]
        for msg in init_messages:
            st.markdown(f"<p style='font-family: Orbitron; color: #00d4ff; text-align: center; font-size: 0.9rem;'>{msg}</p>", unsafe_allow_html=True)
            time.sleep(0.3)
            st.empty()
    st.session_state.initialized = True

# TÍTULO Y SUBTÍTULO
st.title("J.A.R.V.I.S.")
st.caption("Just A Rather Very Intelligent System • Asistente de Tony Stark")

# LÍNEA DIVISORIA ANIMADA
st.markdown("<div class='divider-animated'></div>", unsafe_allow_html=True)

# ESTADO DEL SISTEMA
st.markdown("<p class='system-status'>🟢 SISTEMAS OPERATIVOS • LISTO PARA COMANDOS</p>", unsafe_allow_html=True)

# CONEXIÓN CON GROQ
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("⚠️ Error de configuración: Revisa los 'Secrets' en Streamlit Cloud.")
    st.stop()

# HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🔋" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# PROCESAR MENSAJES
if prompt := st.chat_input("Ingrese su comando, Señor Stark..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Procesar y responder
    with st.chat_message("assistant", avatar="🔋"):
        try:
            mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"⚠️ Señor Stark, detecto una anomalía en el sistema. Permítame investigar: {str(e)}")
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
