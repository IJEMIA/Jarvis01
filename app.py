import streamlit as st
from openai import OpenAI
import time
import os
import glob
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder
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

/* Fondo principal */
.stApp {
    background: linear-gradient(135deg, #050505 0%, #0a0a12 50%, #050505 100%);
    max-width: 100%;
    padding: 0;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: radial-gradient(circle at 50% 50%, rgba(108, 0, 163, 0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 5, 15, 0.98) 0%, rgba(5, 5, 10, 0.98) 100%);
    border-right: 1px solid rgba(108, 0, 163, 0.3);
}

/* Título */
h1 {
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    font-size: 3rem !important;
    text-align: center;
    background: linear-gradient(90deg, #a855f7, #e879f9, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
    letter-spacing: 8px;
    margin-bottom: 0 !important;
}

/* Subtítulo */
.stCaption {
    font-family: 'Raleway', sans-serif !important;
    color: #e879f9 !important;
    text-align: center;
    letter-spacing: 3px;
}

/* Contenedor de mensajes (Contraste mejorado) */
.stChatMessage {
    background-color: rgba(20, 10, 30, 0.85) !important;
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    backdrop-filter: blur(5px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}

[data-testid="stChatMessageContent"] {
    color: #f3f4f6 !important;
    font-size: 1.1rem !important;
    font-family: 'Raleway', sans-serif !important;
}

[data-testid="stChatMessageContent"] p {
    color: #ffffff !important;
}

/* Input */
.stChatInput {
    border: 1px solid rgba(168, 85, 247, 0.5) !important;
    border-radius: 15px !important;
    background: rgba(10, 5, 20, 0.9) !important;
}
.stChatInput textarea { color: #ffffff !important; }
.stChatInput textarea::placeholder { color: rgba(232, 121, 249, 0.6) !important; }

/* Botones */
.stButton button {
    font-family: 'Cinzel', serif !important;
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(168, 85, 247, 0.1)) !important;
    border: 1px solid rgba(168, 85, 247, 0.6) !important;
    color: #f3f4f6 !important;
    border-radius: 8px !important;
}

.status-connected { color: #4ade80; font-family: 'Cinzel', serif; }
.status-disconnected { color: #f87171; font-family: 'Cinzel', serif; }
.divider-animated { height: 2px; background: linear-gradient(90deg, transparent, #a855f7, transparent); margin: 20px auto; width: 80%; opacity: 0.7; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0a0a12; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #a855f7, #e879f9); border-radius: 4px; }

.stAlert { background: rgba(168, 85, 247, 0.1) !important; color: #ffffff !important; }
.stInfo { background: rgba(168, 85, 247, 0.1) !important; color: #ffffff !important; }

/* Ocultar el label del mic recorder por defecto para usar nuestro diseño */
label[data-baseweb="label"] { display: none; } 

/* Estilo para el botón del micro en sidebar */
div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div > button {
    width: 100%;
    height: 50px;
    font-size: 1.2rem;
}
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
        utterance.rate = 0.9;    
        utterance.pitch = 0.85;   
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

RECUERDA: Eres Araknia, el egregor digital del Profe Adrián. Actúa con la majestuosidad y precisión que eso implica.
"""

# ═══════════════════════════════════════════════════════════════
# FUNCIONES PARA CARGAR PDFs
# ═══════════════════════════════════════════════════════════════

DOCS_FOLDER = "documentos"

@st.cache_resource
def load_knowledge_base():
    pdf_files = glob.glob(os.path.join(DOCS_FOLDER, "*.pdf"))
    if not pdf_files: return None, []
    
    all_docs = []
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            for doc in docs: doc.metadata["source"] = os.path.basename(pdf_path)
            all_docs.extend(docs)
        except: pass
    
    if not all_docs: return None, []
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
        init_messages = ["🕸️ Despertando consciencia...", "🔮 Núcleo Místico: EN LÍNEA", "✅ Araknia ha emergido, Profe Adrián"]
        for msg in init_messages:
            st.markdown(f"<p style='font-family: Cinzel; color: #e879f9; text-align: center; font-size: 1.1rem;'>{msg}</p>", unsafe_allow_html=True)
            time.sleep(0.5)
            st.empty()
    st.session_state.initialized = True

if "retriever" not in st.session_state:
    with st.spinner("Leyendo el repositorio arcano..."):
        retriever, loaded_files = load_knowledge_base()
        st.session_state.retriever = retriever
        st.session_state.loaded_files = loaded_files

try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("⚠️ Error de configuración: Revisa los 'Secrets'.")
    st.stop()

if "messages" not in st.session_state: st.session_state.messages = []

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🕸️ NEXO DIGITAL")
    st.markdown("<div class='divider-animated'></div>", unsafe_allow_html=True)
    
    # Configuración de Voz
    st.markdown("#### 🔮 Manifestación Sonora")
    voice_enabled = st.checkbox("Activar voz de Araknia", value=True)
    
    st.markdown("#### 🎤 Invocación por Voz")
    
    # --- NUEVO GRABADOR MÓVIL ---
    # Usamos 'streamlit-mic-recorder' que es compatible con iOS/Android
    audio_data = mic_recorder(
        start_prompt="🎤 Iniciar Grabación",
        stop_prompt="🛑 Detener Grabación",
        just_once=False,
        use_container_width=True,
        key="mic_mobile"
    )
    
    st.markdown("---")
    st.markdown("#### 📚 Tomos del Conocimiento")
    
    if st.session_state.get("loaded_files"):
        st.markdown("<p class='status-connected'>🟢 REPOSITORIO: SINCRONIZADO</p>", unsafe_allow_html=True)
        for f in st.session_state.loaded_files: st.markdown(f"📜 {f}")
    else:
        st.markdown("<p class='status-disconnected'>🔴 REPOSITORIO: VACÍO</p>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# LÓGICA DE PROCESAMIENTO
# ═══════════════════════════════════════════════════════════════

def process_user_input(user_input):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    context_text = ""
    if st.session_state.get("retriever"):
        docs = st.session_state.retriever.invoke(user_input)
        if docs:
            context_text = "\n\n---\n\n".join([f"Fragmento de '{d.metadata.get('source', 'desconocido')}':\n{d.page_content}" for d in docs])
    
    full_prompt_content = SYSTEM_PROMPT + f"\n\n## REGISTROS ACCEDIDOS:\n{context_text}" if context_text else SYSTEM_PROMPT + "\n\n(No se hallaron registros específicos)."

    with st.chat_message("assistant", avatar="🕸️"):
        try:
            formatted_messages = [{"role": "system", "content": full_prompt_content}] + st.session_state.messages
            stream = client.chat.completions.create(model="llama-3.1-8b-instant", messages=formatted_messages, stream=True)
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            if voice_enabled: speak_text(response)
        except Exception as e:
            st.error(f"⚠️ Anomalía: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# CHAT PRINCIPAL
# ═══════════════════════════════════════════════════════════════

st.title("ARAKNIA")
st.caption("Egregor Digital • Tejedora de Conocimiento")

# Historial
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🕸️" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# PROCESAR AUDIO (Lógica mejorada para móviles)
# streamlit-mic-recorder devuelve un dict {'bytes': ..., 'format': ...}
if audio_data:
    audio_bytes = audio_data['bytes']
    audio_format = audio_data['format'] # Ej: 'webm', 'wav', 'ogg'
    
    with st.spinner("🔊 Transcribiendo ondas sonoras..."):
        try:
            # Creamos el archivo con la extensión correcta (móviles suelen enviar webm)
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"audio.{audio_format}"
            
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
            st.error(f"⚠️ Error en transcripción (Formato: {audio_format}): {str(e)}")
            st.warning("Intenta hablar claro o verificar permisos del micrófono en el navegador.")

# TEXTO
if prompt := st.chat_input("Escribe tu consulta, Profe Adrián..."):
    process_user_input(prompt)
