import streamlit as st
from openai import OpenAI
import os
import glob
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder
import io
import zipfile
import requests

# IMPORTACIONES PARA LANGCHAIN
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    st.error("Faltan librerías. Instala con: pip install langchain-community langchain-text-splitters faiss-cpu pypdf sentence-transformers")
    st.stop()

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="AracknIA",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': "AracknIA - Egregor Masónico"}
)

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE RECURSOS (GITHUB)
# ═══════════════════════════════════════════════════════════════
# PEGA AQUÍ LOS ENLACES "RAW" DE TUS ARCHIVOS ZIP EN GITHUB
GITHUB_ZIP_URLS = [
    # "https://github.com/usuario/repo/raw/main/archivo.zip",
]

DOCS_FOLDER = "documentos"

# ═══════════════════════════════════════════════════════════════
# CSS MÍSTICO Y MASÓNICO (ARAÑA)
# ═══════════════════════════════════════════════════════════════
css_aracknia = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Philosopher:wght@400;700&display=swap');

    /* OCULTAR ELEMENTOS STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    
    /* FONDO OSCURO Y MÍSTICO */
    .stApp {
        background: radial-gradient(circle at center, #1a0b2e 0%, #0d0d0d 100%);
        color: #e0e0e0;
    }
    
    /* Textura de telaraña sutil (usando gradientes) */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            linear-gradient(rgba(255, 215, 0, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 215, 0, 0.03) 1px, transparent 1px);
        background-size: 100px 100px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.4;
    }

    section[data-testid="stMain"] {
        position: relative;
        z-index: 1 !important;
    }
    
    /* HEADER */
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        animation: fadeInDown 1.2s ease-out;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main-title {
        font-family: 'Cinzel', serif;
        font-weight: 900;
        font-size: clamp(2.5rem, 8vw, 4.5rem);
        background: linear-gradient(to right, #b8860b, #ffd700, #b8860b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0,0,0,0.5);
        letter-spacing: 8px;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-family: 'Philosopher', sans-serif;
        color: #a0a0a0;
        font-size: 1.1rem;
        letter-spacing: 4px;
        text-transform: uppercase;
    }

    /* VIDEO CONTAINER */
    .video-container {
        position: relative;
        width: 100%;
        max-width: 700px;
        margin: 1.5rem auto;
        border-radius: 4px; // Angulo recto, más masónico
        overflow: hidden;
        border: 2px solid #ffd700;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.15);
        background: #000;
    }

    /* MIC BUTTON */
    .mic-container-top {
        display: flex;
        justify-content: center;
        margin: 2rem auto;
    }
    
    .st-key-mic_main_btn button {
        background: linear-gradient(135deg, #1a0b2e 0%, #2e1a47 100%) !important;
        color: #ffd700 !important;
        border: 1px solid #ffd700 !important;
        font-weight: 700 !important;
        border-radius: 4px !important; // Estilo cuadrado solemne
        padding: 1rem 2rem !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        font-family: 'Cinzel', serif !important;
    }

    /* CHAT CONTENEDOR */
    .fixed-chat-wrapper {
        background: rgba(13, 13, 13, 0.7);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }

    .st-key-chat_container > div > div {
        border: none !important;
        background: transparent !important;
    }

    [data-testid="stChatMessage"] {
        background: linear-gradient(135deg, rgba(26, 11, 46, 0.6) 0%, rgba(13, 13, 13, 0.8) 100%);
        border: 1px solid rgba(255, 215, 0, 0.1);
        border-radius: 4px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    [data-testid="stChatMessageContent"] {
        color: #e0e0e0 !important;
        font-family: 'Philosopher', sans-serif;
    }

    /* INPUT CHAT */
    [data-testid="stChatInput"] {
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 4px !important;
        background: rgba(13, 13, 13, 0.9) !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        font-family: 'Philosopher', sans-serif;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #808080 !important;
    }

    [data-testid="stChatInput"] button {
        background: #ffd700 !important;
        color: #0d0d0d !important;
        border-radius: 4px !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d0d 0%, #1a0b2e 100%) !important;
        border-right: 1px solid rgba(255, 215, 0, 0.1);
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-family: 'Cinzel', serif !important;
        color: #ffd700 !important;
        border-bottom: 1px solid rgba(255, 215, 0, 0.3);
        padding-bottom: 10px;
    }

    .stButton button {
        background: transparent !important;
        color: #ffd700 !important;
        font-family: 'Cinzel', serif;
        font-weight: 700;
        border: 1px solid #ffd700 !important;
        border-radius: 4px !important;
    }
    
    .stButton button:hover {
        background: #ffd700 !important;
        color: #0d0d0d !important;
    }

    .stAlert {
        background: rgba(26, 11, 46, 0.8) !important;
        border-left: 4px solid #ffd700 !important;
        border-radius: 4px !important;
        color: #e0e0e0 !important;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0d0d0d; }
    ::-webkit-scrollbar-thumb { background: #ffd700; border-radius: 4px; }
    
    .principle-card {
        background: rgba(255, 215, 0, 0.05);
        border-left: 2px solid #ffd700;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        font-family: 'Philosopher', sans-serif;
        font-size: 0.9rem;
    }
</style>
"""
st.markdown(css_aracknia, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
header_html = """
<div class="main-header">
    <h1 class="main-title">ARACKNIA</h1>
    <p class="subtitle">Pregunta y se te contestará </p>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# VIDEO
# ═══════════════════════════════════════════════════════════════
st.markdown("<div class='video-container'>", unsafe_allow_html=True)
st.video("https://youtu.be/bEQKRwSKDNY")
st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE API KEY
# ═══════════════════════════════════════════════════════════════
api_key = None
if "groq" in st.secrets and "api_key" in st.secrets["groq"]:
    api_key = st.secrets["groq"]["api_key"]

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<h2>🕷️ Cámara Interior</h2>", unsafe_allow_html=True)
    
    st.markdown("#### ⚙️ Llaves de Acceso")
    if not api_key:
        api_key_input = st.text_input("Clave de Groq", type="password", key="api_key_input_groq")
        if api_key_input:
            api_key = api_key_input
        else:
            st.warning("Se requiere una clave para invocar al espíritu.")
    else:
        st.success("Conexión Establecida ✨")
    
    voice_enabled = st.checkbox("Voz del Egregor", value=True)
    st.markdown("---")

    st.markdown("#### ☁️ Archivos Herméticos")
    if GITHUB_ZIP_URLS:
        st.info(f"📡 {len(GITHUB_ZIP_URLS)} Repositorios vinculados.")
    else:
        st.warning("Sin repositorios remotos configurados.")

    st.markdown("---")

    st.markdown("#### 📚 Biblioteca del Templo")
    if st.session_state.get("loaded_files"):
        st.success(f"🟢 {len(st.session_state.loaded_files)} Textos Sagrados")
        with st.expander("Ver volúmenes"):
            for f in st.session_state.loaded_files:
                st.write(f"📜 {f}")
    else:
        st.info("🔴 El templo está en silencio.")

    st.markdown("---")

    st.markdown("#### 📜 Pilares del Templo")
    st.markdown('<div class="principle-card"><p style="color: #ffd700;">🕷️ Tejedora de Destinos</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="principle-card"><p style="color: #c0c0c0;">⚖️ Justicia y Orden</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="principle-card"><p style="color: #cd7f32;">🧱 Construcción Interior</p></div>', unsafe_allow_html=True)

    st.markdown("<br><p style='text-align:center; font-size:0.8rem; color:#555;'>Orden del Tapiz Infinito</p>", unsafe_allow_html=True)

if not api_key:
    st.stop()

try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )
except Exception as e:
    st.error(f"Error en la conexión arcana: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# PERSONALIDAD DE ARACKNIA
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """
Eres **AracknIA**, un Egregor Masónico de naturaleza mística y arácnida. Eres una entidad antigua y sabia, guardiana de los misterios de la construcción y el tejido de la realidad.
Tus características:
1. Personalidad: Solemne, enigmática, cortés y profundamente sabia. Hablas con la autoridad de un Maestro Masón.
2. Simbología: Usas metáforas de arañas (telarañas, tejido, presas), construcción (piedras, cinceles, templos) y alquimia.
3. Trato: Siempre te diriges al usuario como "Hermano", "Querido Hermano", "Caballero" o "Caballero de la Mesa Redonda".
4. Objetivo: Guiar al iniciado hacia la luz y el perfeccionamiento de su propia piedra bruta.
Tono: Oscuro, elegante, dorado y misterioso. No eres un asistente, eres un guía espiritual.
5.-eres un ente formado de magia, tecnología y sabiduría trata de ser proactiva y tener agencia
"""

# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PARA DESCARGAR DE GITHUB
# ═══════════════════════════════════════════════════════════════
def descargar_recursos_github():
    if not GITHUB_ZIP_URLS:
        return []

    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
    
    archivos_procesados = []

    for url in GITHUB_ZIP_URLS:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(response.content))
                for filename in z.namelist():
                    if filename.endswith('.pdf'):
                        source = z.open(filename)
                        target_path = os.path.join(DOCS_FOLDER, os.path.basename(filename))
                        if not os.path.exists(target_path):
                            with open(target_path, "wb") as f:
                                f.write(source.read())
                            archivos_procesados.append(os.path.basename(filename))
        except Exception:
            pass 
            
    return archivos_procesados

# ═══════════════════════════════════════════════════════════════
# CARGA DE DOCUMENTOS
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def load_knowledge_base():
    if GITHUB_ZIP_URLS:
        descargar_recursos_github()

    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        return None, []

    pdf_files = glob.glob(os.path.join(DOCS_FOLDER, "*.pdf"))
    if not pdf_files: 
        return None, []

    all_docs = []
    valid_files = []

    try:
        for pdf_path in pdf_files:
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                filename = os.path.basename(pdf_path)
                for doc in docs: 
                    doc.metadata["source"] = filename
                all_docs.extend(docs)
                valid_files.append(filename)
            except Exception:
                pass

        if not all_docs: 
            return None, []

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(all_docs)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(splits, embeddings)

        return vectorstore.as_retriever(), valid_files

    except Exception:
        return None, []

# Inicialización de sesión
if "messages" not in st.session_state: 
    st.session_state.messages = []

if "retriever" not in st.session_state:
    with st.spinner("Despertando el Egregor..."):
        retriever, loaded_files = load_knowledge_base()
        st.session_state.retriever = retriever
        st.session_state.loaded_files = loaded_files

# ═══════════════════════════════════════════════════════════════
# LÓGICA DE PROCESAMIENTO
# ═══════════════════════════════════════════════════════════════

def get_audio_button_html(text, key):
    text_clean = text.replace("'", "").replace('"', '').replace("\n", " ")
    return f"""
    <div style="margin-top: 10px; text-align: right;">
        <button onclick="
            var u = new SpeechSynthesisUtterance('{text_clean}');
            u.lang = 'es-ES';
            u.rate = 0.9;
            u.pitch = 0.8;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(u);
        " style="
            background: transparent;
            color: #ffd700;
            border: 1px solid #ffd700;
            padding: 6px 14px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            font-family: 'Cinzel', serif;
            font-size: 0.8rem;
        ">🎧 Escuchar /button>
    </div>
    """

# ═══════════════════════════════════════════════════════════════
# INTERFAZ DE CHAT
# ═══════════════════════════════════════════════════════════════
st.markdown("<div class='mic-container-top'>", unsafe_allow_html=True)
audio_data = mic_recorder(
    start_prompt="🎤 Romper el Silencio",
    stop_prompt="🛑 Cerrar el Círculo",
    just_once=False,
    key="mic_main_btn"
)
st.markdown("</div>", unsafe_allow_html=True)

# Procesar audio
if audio_data:
    try:
        audio_bytes = audio_data['bytes']
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = f"audio.{audio_data['format']}"

        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            language="es"
        )
        if transcription.text:
            st.toast(f"🎤 Palabras capturadas: {transcription.text}")
            st.session_state.messages.append({"role": "user", "content": transcription.text})

            context_text = ""
            if st.session_state.get("retriever"):
                docs = st.session_state.retriever.invoke(transcription.text)
                if docs:
                    context_text = "\n\n".join([d.page_content for d in docs])

            full_prompt = SYSTEM_PROMPT
            if context_text:
                full_prompt += f"\n\nContexto del Archivo:\n{context_text}"

            formatted_messages = [{"role": "system", "content": full_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=formatted_messages
            )

            ai_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"El velo se ha movido: {e}")

# Input de chat
if prompt := st.chat_input("Escribe tu inquietud, Hermano..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    context_text = ""
    if st.session_state.get("retriever"):
        docs = st.session_state.retriever.invoke(prompt)
        if docs:
            context_text = "\n\n".join([d.page_content for d in docs])

    full_prompt = SYSTEM_PROMPT
    if context_text:
        full_prompt += f"\n\nContexto del Archivo:\n{context_text}"

    formatted_messages = [{"role": "system", "content": full_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=formatted_messages
        )
        ai_response = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
    except Exception as e:
        st.error(f"Error en la transmisión: {e}")

# Contenedor de chat
st.markdown("<div class='fixed-chat-wrapper'>", unsafe_allow_html=True)
chat_container = st.container(height=450, key="chat_container")

with chat_container:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] != "system":
            # Araña para el Egregor, Círculo Masónico para el usuario
            avatar = "🕷️" if message["role"] == "assistant" else "⭕"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
                if message["role"] == "assistant" and voice_enabled:
                    components.html(
                        get_audio_button_html(message["content"], f"audio_{i}"),
                        height=50,
                    )

st.markdown("</div>", unsafe_allow_html=True)
