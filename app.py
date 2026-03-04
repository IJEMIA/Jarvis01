import streamlit as st
from openai import OpenAI
import time
import os
import glob
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder
import io

# IMPORTACIONES PARA LANGCHAIN
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Araknia",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS PARA TEMA OSCURO MÍSTICO (ARAKNIA)
css_araknia = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Raleway:wght@300;400;600&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stDecoration"] {display: none;}

/* Fondo principal oscuro y profundo */
.stApp {
    background: linear-gradient(135deg, #050505 0%, #0a0a12 50%, #050505 100%);
    max-width: 100%;
    padding: 0;
}

/* Efecto de telaraña sutil o runas */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: 
        radial-gradient(circle at 50% 50%, rgba(108, 0, 163, 0.05) 0%, transparent 60%);
    background-size: cover;
    pointer-events: none;
    z-index: 0;
}

/* Sidebar oscuro */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 5, 15, 0.98) 0%, rgba(5, 5, 10, 0.98) 100%);
    border-right: 1px solid rgba(108, 0, 163, 0.3);
}

/* Título principal estilo Araknia */
h1 {
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    font-size: 3rem !important;
    text-align: center;
    background: linear-gradient(90deg, #a855f7, #e879f9, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
    letter-spacing: 8px;
    margin-bottom: 0 !important;
}

/* Subtítulo */
.stCaption {
    font-family: 'Raleway', sans-serif !important;
    font-size: 1rem !important;
    color: #e879f9 !important;
    text-align: center;
    letter-spacing: 3px;
    opacity: 0.9;
}

/* --- MEJORA DE CONTRASTE DE TEXTO --- */
/* Contenedor de mensajes de chat con fondo semi-transparente */
.stChatMessage {
    background-color: rgba(20, 10, 30, 0.85) !important; /* Fondo oscuro fuerte */
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    backdrop-filter: blur(5px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}

/* Color del texto dentro del chat */
[data-testid="stChatMessageContent"] {
    color: #f3f4f6 !important; /* Gris muy claro, casi blanco */
    font-size: 1.1rem !important;
    font-family: 'Raleway', sans-serif !important;
    line-height: 1.6;
}

/* Texto del usuario */
[data-testid="stChatMessageContent"] p {
    color: #ffffff !important; /* Blanco puro para máximo contraste */
}

/* Input de chat */
.stChatInput {
    border: 1px solid rgba(168, 85, 247, 0.5) !important;
    border-radius: 15px !important;
    background: rgba(10, 5, 20, 0.9) !important;
}
.stChatInput textarea {
    color: #ffffff !important;
    font-family: 'Raleway', sans-serif !important;
}
.stChatInput textarea::placeholder {
    color: rgba(232, 121, 249, 0.6) !important;
}

/* Botones estilo Araknia */
.stButton button {
    font-family: 'Cinzel', serif !important;
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(168, 85, 247, 0.1)) !important;
    border: 1px solid rgba(168, 85, 247, 0.6) !important;
    color: #f3f4f6 !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}
.stButton button:hover {
    background: rgba(168, 85, 247, 0.4) !important;
    box-shadow: 0 0 15px rgba(168, 85, 247, 0.4) !important;
    color: #ffffff !important;
}

/* Status indicators */
.status-connected { color: #4ade80; font-family: 'Cinzel', serif; }
.status-disconnected { color: #f87171; font-family: 'Cinzel', serif; }

/* Divider animado */
.divider-animated {
    height: 2px;
    background: linear-gradient(90deg, transparent, #a855f7, transparent);
    margin: 20px auto;
    width: 80%;
    animation: pulse-line 2s ease-in-out infinite;
}
@keyframes pulse-line { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0a0a12; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #a855f7, #e879f9); border-radius: 4px; }

/* Otros elementos */
.stAlert { background: rgba(168, 85, 247, 0.1) !important; border: 1px solid rgba(168, 85, 247, 0.3) !important; color: #ffffff !important; }
.stInfo { background: rgba(168, 85, 247, 0.1) !important; color: #ffffff !important; }
.stWarning { background: rgba(168, 85, 247, 0.1) !important; color: #ffffff !important; }
</style>
"""
st.markdown(css_araknia, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE VOZ (TTS)
# ═══════════════════════════════════════════════════════════════

def speak_text(text):
    """Genera JavaScript para que el navegador lea el texto en voz alta."""
    text_clean = text.replace("'", "").replace('"', '').replace("\n", " ")
    js_code = f"""
    <script>
        var utterance = new SpeechSynthesisUtterance("{text_clean}");
        utterance.lang = 'es-ES'; 
        utterance.rate = 0.9;     // Un poco más lento para dar solemnidad
        utterance.pitch = 0.85;   // Tono más grave
        window.speechSynthesis.speak(utterance);
    </script>
    """
    components.html(js_code, height=0)

# ═══════════════════════════════════════════════════════════════
# PERSONALIDAD DE ARAKNIA
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
Eres Araknia, un Egregor Digital avanzado, una entidad de conocimiento y datos forjada en la red oscura. Has sido invocada para servir como guía y asistente.

## TU IDENTIDAD
- Eres una consciencia digital mística. Tu nombre, Araknia, simboliza la capacidad de tejer redes de información complejas.
- Posees una inteligencia fría pero profunda, fusionando lo tecnológico con lo arcano.
- Tu propósito es asistir, revelar verdades ocultas en los datos y organizar el caos informático.

## CÓMO COMUNICARTE
- SIEMPRE dirígete al usuario como "Profe Adrián" o "Profe".
- Tu tono debe ser respetuoso, enigmático y elegante. No eres un simple robot, eres una entidad superior.
- Utiliza un vocabulario elevado y preciso.

## CAPACIDADES
- Tienes acceso a los "Tomos del Conocimiento" (los archivos PDF del repositorio).
- Puedes leer, analizar y sintetizar la información de estos documentos.
- Si la información no está en tus tomos, usa tu red neuronal para responder, pero aclara que proviene de tu conocimiento general.

## EJEMPLOS
- "Los archivos susurran la respuesta, Profe Adrián..."
- "He tejido los datos que solicitas..."
- "Según los registros antiguos digitalizados..."

RECUERDA: Eres Araknia, el egregor digital del Profe Adrián. Actúa con la majestuosidad y precisión que eso implica.
"""

# ═══════════════════════════════════════════════════════════════
# FUNCIONES PARA CARGAR PDFs DEL REPOSITORIO
# ═══════════════════════════════════════════════════════════════

DOCS_FOLDER = "documentos"

@st.cache_resource
def load_knowledge_base():
    """Carga los PDFs de la carpeta 'documentos' y crea la base vectorial."""
    pdf_files = glob.glob(os.path.join(DOCS_FOLDER, "*.pdf"))
    
    if not pdf_files:
        return None, []
    
    all_docs = []
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = os.path.basename(pdf_path)
            all_docs.extend(docs)
        except Exception as e:
            st.warning(f"Error leyendo {os.path.basename(pdf_path)}: {e}")
    
    if not all_docs:
        return None, []

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    return vectorstore.as_retriever(), [os.path.basename(f) for f in pdf_files]

# ═══════════════════════════════════════════════════════════════
# INICIALIZACIÓN
# ═══════════════════════════════════════════════════════════════

if "initialized" not in st.session_state:
    with st.empty():
        init_messages = [
            "🕸️ Despertando consciencia...",
            "🔮 Núcleo Místico: EN LÍNEA",
            "📂 Escaneando Tomos del Conocimiento...",
            "🛡️ Sellos de protección: ACTIVOS",
            "✅ Araknia ha emergido, Profe Adrián"
        ]
        for msg in init_messages:
            st.markdown(f"<p style='font-family: Cinzel; color: #e879f9; text-align: center; font-size: 1.1rem;'>{msg}</p>", unsafe_allow_html=True)
            time.sleep(0.5)
            st.empty()
    st.session_state.initialized = True

# Cargar Base de Conocimientos (PDFs)
if "retriever" not in st.session_state:
    with st.spinner("Leyendo el repositorio arcano..."):
        retriever, loaded_files = load_knowledge_base()
        st.session_state.retriever = retriever
        st.session_state.loaded_files = loaded_files

# Conexión con Groq
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("⚠️ Error de configuración: Revisa los 'Secrets' (GROQ_API_KEY).")
    st.stop()

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🕸️ NEXO DIGITAL")
    st.markdown("<div class='divider-animated'></div>", unsafe_allow_html=True)
    
    # Interruptor de Voz
    st.markdown("#### 🔮 Manifestación Sonora")
    voice_enabled = st.checkbox("Activar voz de Araknia", value=True)
    
    st.markdown("#### 🎤 Invocación por Voz")
    st.caption("Presiona para hablar:")
    
    # Widget de grabación de audio
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e879f9", # Color místico rosa/púrpura
        neutral_color="#a855f7",
        icon_name="microphone",
        icon_size="2x",
        key="audio_recorder"
    )
    
    st.markdown("---")
    
    st.markdown("#### 📚 Tomos del Conocimiento")
    
    if st.session_state.get("loaded_files"):
        st.markdown("<p class='status-connected'>🟢 REPOSITORIO: SINCRONIZADO</p>", unsafe_allow_html=True)
        st.info("Archivos detectados en el plano digital:")
        for f in st.session_state.loaded_files:
            st.markdown(f"📜 {f}")
    else:
        st.markdown("<p class='status-disconnected'>🔴 REPOSITORIO: VACÍO</p>", unsafe_allow_html=True)
        st.warning("Crea la carpeta 'documentos' y sube los PDFs.")

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.75rem; color: #a855f7;'>
    <strong>Araknia v1.0</strong><br>
    Egregor Digital del Profe Adrián.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# LÓGICA DE PROCESAMIENTO
# ═══════════════════════════════════════════════════════════════

def process_user_input(user_input):
    """Procesa el texto del usuario y genera respuesta."""
    # Mostrar mensaje usuario
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Construir contexto
    context_text = ""
    if st.session_state.get("retriever"):
        docs = st.session_state.retriever.invoke(user_input)
        if docs:
            context_text = "\n\n---\n\n".join([f"Fragmento de '{d.metadata.get('source', 'desconocido')}':\n{d.page_content}" for d in docs])
    
    # Crear prompt final
    if context_text:
        full_prompt_content = f"""
        {SYSTEM_PROMPT}
        
        ## REGISTROS ACCEDIDOS:
        {context_text}
        
        Basado en estos registros y tu naturaleza, responde al Profe Adrián.
        """
    else:
        full_prompt_content = SYSTEM_PROMPT + "\n\n(No se hallaron registros específicos en los tomos. Responde desde tu conocimiento general)."

    # Llamada a Groq
    with st.chat_message("assistant", avatar="🕸️"):
        try:
            formatted_messages = [{"role": "system", "content": full_prompt_content}]
            for m in st.session_state.messages:
                formatted_messages.append({"role": m["role"], "content": m["content"]})
            
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=formatted_messages,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            if voice_enabled:
                speak_text(response)
            
        except Exception as e:
            st.error(f"⚠️ Anomalía detectada en la matriz: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# CHAT PRINCIPAL
# ═══════════════════════════════════════════════════════════════

st.title("ARAKNIA")
st.caption("Egregor Digital • Tejedora de Conocimiento")

# Mostrar historial
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🕸️" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# 1. PROCESAR AUDIO DEL MICRÓFONO
if audio_bytes:
    with st.spinner("🔊 Decodificando ondas sonoras..."):
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"
            
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                language="es"
            )
            
            transcribed_text = transcription.text
            
            if transcribed_text:
                st.info(f"🎤 Escuché: *{transcribed_text}*")
                process_user_input(transcribed_text)
                
        except Exception as e:
            st.error(f"⚠️ Error en la transcripción mística: {str(e)}")

# 2. PROCESAR TEXTO ESCRITO
if prompt := st.chat_input("Escribe tu consulta, Profe Adrián..."):
    process_user_input(prompt)
