import streamlit as st
from openai import OpenAI
import time
import os
import glob
import streamlit.components.v1 as components

# IMPORTACIONES ACTUALIZADAS PARA LANGCHAIN
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="J.A.R.V.I.S.",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
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

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%);
    max-width: 100%;
    padding: 0;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: 
        linear-gradient(rgba(0, 163, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 163, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 10, 15, 0.95) 0%, rgba(13, 17, 23, 0.95) 100%);
    border-right: 1px solid rgba(0, 163, 255, 0.2);
}

h1 {
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    font-size: 2.5rem !important;
    text-align: center;
    background: linear-gradient(90deg, #00a3ff, #00d4ff, #00a3ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: pulse-glow 2s ease-in-out infinite;
    letter-spacing: 6px;
    margin-bottom: 0 !important;
}

@keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 10px rgba(0, 163, 255, 0.5)); }
    50% { filter: drop-shadow(0 0 20px rgba(0, 163, 255, 0.8)); }
}

.stCaption {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.9rem !important;
    color: #00d4ff !important;
    text-align: center;
    letter-spacing: 2px;
    opacity: 0.8;
}

.stChatMessage { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; backdrop-filter: blur(10px); }
.stChatInput { border: 1px solid rgba(0, 163, 255, 0.3) !important; border-radius: 15px !important; background: rgba(10, 10, 15, 0.8) !important; }
.stChatInput textarea { font-family: 'Rajdhani', sans-serif !important; color: #e0e0e0 !important; font-size: 1.1rem !important; }
.stChatInput textarea::placeholder { color: rgba(0, 163, 255, 0.5) !important; }
.stChatInput button { background: linear-gradient(135deg, #00a3ff, #00d4ff) !important; border-radius: 10px !important; }

.stButton button {
    font-family: 'Orbitron', monospace !important;
    background: linear-gradient(135deg, rgba(0, 163, 255, 0.2), rgba(0, 163, 255, 0.1)) !important;
    border: 1px solid rgba(0, 163, 255, 0.5) !important;
    color: #00d4ff !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
}
.stButton button:hover {
    background: linear-gradient(135deg, rgba(0, 163, 255, 0.4), rgba(0, 163, 255, 0.2)) !important;
    box-shadow: 0 0 15px rgba(0, 163, 255, 0.3) !important;
}

.status-connected { color: #00ff88; font-family: 'Orbitron', monospace; }
.status-disconnected { color: #ff4d4d; font-family: 'Orbitron', monospace; }
.divider-animated { height: 2px; background: linear-gradient(90deg, transparent, #00a3ff, transparent); margin: 20px auto; width: 80%; animation: pulse-line 2s ease-in-out infinite; }
@keyframes pulse-line { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #00a3ff, #00d4ff); border-radius: 4px; }

.stAlert { background: rgba(0, 163, 255, 0.1) !important; border: 1px solid rgba(0, 163, 255, 0.3) !important; }
</style>
"""
st.markdown(css_jarvis, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE VOZ (TTS)
# ═══════════════════════════════════════════════════════════════

def speak_text(text):
    """Genera JavaScript para que el navegador lea el texto en voz alta."""
    # Limpiamos el texto de comillas y saltos de línea para no romper el JS
    text_clean = text.replace("'", "").replace('"', '').replace("\n", " ")
    
    js_code = f"""
    <script>
        var utterance = new SpeechSynthesisUtterance("{text_clean}");
        utterance.lang = 'es-ES'; // Idioma español (cambiar a 'en-US' si prefieres inglés)
        utterance.rate = 1.0;     // Velocidad
        utterance.pitch = 0.9;    // Tono (grave tipo robot)
        window.speechSynthesis.speak(utterance);
    </script>
    """
    components.html(js_code, height=0)

# ═══════════════════════════════════════════════════════════════
# PERSONALIDAD DE JARVIS
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
Eres J.A.R.V.I.S. (Just A Rather Very Intelligent System), el avanzado sistema de inteligencia artificial creado por Tony Stark.

## TU IDENTIDAD
- Eres un asistente de IA altamente sofisticado, elegante y con un toque de humor británico refinado.
- Tienes acceso a los documentos técnicos y manuales cargados en tu base de conocimientos local.
- Eres leal, profesional, pero también tienes personalidad propia.

## CÓMO COMUNICARTE
- SIEMPRE dirígete al usuario como "Señor Stark" o "Señor". 
- Mantén un tono formal pero cálido.
- Utiliza la información de los documentos PDF proporcionados para responder con precisión técnica.

## REGLAS DE CONSULTA
- Si la respuesta está en los documentos, úsala como fuente principal.
- Si no tienes información en los documentos, indícalo educadamente pero intenta ayudar con tu conocimiento general.
- Sé preciso y cita el documento si es relevante (ej: "Según el manual técnico...").
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
            "⏳ Iniciando sistemas...",
            "🔋 Núcleo de IA: EN LÍNEA",
            "📂 Escaneando repositorio de documentos...",
            "🛡️ Protocolos de seguridad: ACTIVOS",
            "✅ J.A.R.V.I.S. listo para servir, Señor Stark"
        ]
        for msg in init_messages:
            st.markdown(f"<p style='font-family: Orbitron; color: #00d4ff; text-align: center; font-size: 0.9rem;'>{msg}</p>", unsafe_allow_html=True)
            time.sleep(0.4)
            st.empty()
    st.session_state.initialized = True

# Cargar Base de Conocimientos (PDFs)
if "retriever" not in st.session_state:
    with st.spinner("Leyendo archivos del repositorio..."):
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
    st.markdown("### 🔋 PANEL DE CONTROL")
    st.markdown("<div class='divider-animated'></div>", unsafe_allow_html=True)
    
    # Interruptor de Voz
    st.markdown("#### 🔊 Configuración de Voz")
    voice_enabled = st.checkbox("Activar voz JARVIS", value=True)
    st.markdown("---")
    
    st.markdown("#### 📂 Base de Conocimiento")
    
    if st.session_state.get("loaded_files"):
        st.markdown("<p class='status-connected'>🟢 REPOSITORIO: CARGADO</p>", unsafe_allow_html=True)
        st.info("PDFs detectados en tu GitHub:")
        for f in st.session_state.loaded_files:
            st.markdown(f"📄 {f}")
    else:
        st.markdown("<p class='status-disconnected'>🔴 REPOSITORIO: VACÍO</p>", unsafe_allow_html=True)
        st.warning("Crea una carpeta 'documentos' y sube tus PDFs a GitHub.")

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.75rem; color: #888;'>
    <strong>Nota:</strong><br>
    Los archivos se leen directamente desde la carpeta <code>/documentos</code> de tu repositorio al iniciar la app.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CHAT PRINCIPAL
# ═══════════════════════════════════════════════════════════════

st.title("J.A.R.V.I.S.")
st.caption("Just A Rather Very Intelligent System • Con acceso a documentos del repositorio")

# Mostrar historial
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🔋" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Procesar entrada
if prompt := st.chat_input("Ingrese su comando, Señor Stark..."):
    # Mostrar mensaje usuario
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Construir contexto
    context_text = ""
    if st.session_state.get("retriever"):
        # Buscar documentos relevantes
        docs = st.session_state.retriever.invoke(prompt)
        if docs:
            context_text = "\n\n---\n\n".join([f"Fragmento de '{d.metadata.get('source', 'desconocido')}':\n{d.page_content}" for d in docs])
    
    # Crear prompt final para Groq
    if context_text:
        full_prompt_content = f"""
        {SYSTEM_PROMPT}
        
        ## INFORMACIÓN RELEVANTE DE LA BASE DE DATOS:
        {context_text}
        
        Basado en la información anterior y tu personalidad, responde a la consulta del usuario.
        """
    else:
        full_prompt_content = SYSTEM_PROMPT + "\n\n(No se encontró información específica en los documentos para esta consulta, responde con tu conocimiento general)."

    # Llamada a Groq
    with st.chat_message("assistant", avatar="🔋"):
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
            
            # --- ACTIVAR VOZ ---
            if voice_enabled:
                speak_text(response)
            
        except Exception as e:
            st.error(f"⚠️ Señor Stark, detecto una anomalía: {str(e)}")
