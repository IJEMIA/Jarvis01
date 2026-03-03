    import streamlit as st
from openai import OpenAI
import time
import os
import tempfile
from datetime import datetime

# GOOGLE DRIVE IMPORTS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

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

/* Sidebar personalizado */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 10, 15, 0.95) 0%, rgba(13, 17, 23, 0.95) 100%);
    border-right: 1px solid rgba(0, 163, 255, 0.2);
}

[data-testid="stSidebar"] .element-container {
    font-family: 'Rajdhani', sans-serif;
}

[data-testid="stSidebarHeader"] {
    font-family: 'Orbitron', monospace;
}

/* Título principal estilo Jarvis */
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

/* Subtítulo */
.stCaption {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.9rem !important;
    color: #00d4ff !important;
    text-align: center;
    letter-spacing: 2px;
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
[data-testid="stChatMessageContent"] {
    font-family: 'Rajdhani', sans-serif;
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

/* Botones estilo Jarvis */
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

/* Selectbox estilo Jarvis */
.stSelectbox label {
    font-family: 'Orbitron', monospace !important;
    color: #00d4ff !important;
    font-size: 0.85rem !important;
}

/* Archivos listados */
.file-item {
    background: rgba(0, 163, 255, 0.1);
    border: 1px solid rgba(0, 163, 255, 0.3);
    border-radius: 8px;
    padding: 10px;
    margin: 5px 0;
    transition: all 0.3s ease;
}

.file-item:hover {
    background: rgba(0, 163, 255, 0.2);
    border-color: rgba(0, 163, 255, 0.5);
}

/* Status indicators */
.status-connected {
    color: #00ff88;
    font-family: 'Orbitron', monospace;
}

.status-disconnected {
    color: #ff4d4d;
    font-family: 'Orbitron', monospace;
}

/* Divider animado */
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

/* Expander styling */
.streamlit-expanderHeader {
    font-family: 'Orbitron', monospace !important;
    background: rgba(0, 163, 255, 0.1) !important;
    border: 1px solid rgba(0, 163, 255, 0.3) !important;
    border-radius: 8px !important;
}

/* Info boxes */
.stAlert {
    background: rgba(0, 163, 255, 0.1) !important;
    border: 1px solid rgba(0, 163, 255, 0.3) !important;
}

/* Text input and textarea */
.stTextInput input, .stTextArea textarea {
    background: rgba(10, 10, 15, 0.8) !important;
    border: 1px solid rgba(0, 163, 255, 0.3) !important;
    color: #e0e0e0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
</style>
"""
st.markdown(css_jarvis, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE GOOGLE DRIVE
# ═══════════════════════════════════════════════════════════════

# SCOPES para Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def init_drive_service():
    """Inicializa el servicio de Google Drive usando Service Account"""
    try:
        # Intentar obtener credenciales de secrets
        if "google_credentials" in st.secrets:
            creds_dict = dict(st.secrets["google_credentials"])
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES
            )
            service = build('drive', 'v3', credentials=creds)
            return service
        else:
            return None
    except Exception as e:
        st.error(f"Error conectando con Drive: {str(e)}")
        return None

def list_drive_files(service, folder_id=None, file_types=None):
    """Lista archivos de Google Drive"""
    try:
        query_parts = []
        query_parts.append("trashed = false")
        
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        
        if file_types:
            mime_queries = [f"mimeType contains '{ft}'" for ft in file_types]
            query_parts.append(f"({(' or '.join(mime_queries))})")
        
        query = " and ".join(query_parts)
        
        results = service.files().list(
            q=query,
            pageSize=50,
            fields="files(id, name, mimeType, size, modifiedTime, webViewLink)"
        ).execute()
        
        return results.get('files', [])
    except Exception as e:
        st.error(f"Error listando archivos: {str(e)}")
        return []

def download_file(service, file_id, file_name):
    """Descarga un archivo de Google Drive"""
    try:
        request = service.files().get_media(fileId=file_id)
        
        # Crear directorio temporal si no existe
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_name)
        
        with io.FileIO(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
        return file_path
    except Exception as e:
        st.error(f"Error descargando archivo: {str(e)}")
        return None

def read_file_content(file_path, mime_type):
    """Lee el contenido de un archivo según su tipo"""
    try:
        content = ""
        
        if 'pdf' in mime_type:
            # Para PDFs necesitarías PyPDF2 o similar
            content = f"[Archivo PDF: {os.path.basename(file_path)}]"
            
        elif 'spreadsheet' in mime_type or 'excel' in mime_type:
            content = f"[Archivo Excel: {os.path.basename(file_path)}]"
            
        elif 'document' in mime_type or 'word' in mime_type:
            content = f"[Documento Word: {os.path.basename(file_path)}]"
            
        elif 'text' in mime_type or file_path.endswith(('.txt', '.md', '.py', '.js', '.json', '.csv')):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
        else:
            content = f"[Archivo: {os.path.basename(file_path)} - Tipo: {mime_type}]"
            
        return content
    except Exception as e:
        return f"Error leyendo archivo: {str(e)}"

# ═══════════════════════════════════════════════════════════════
# PERSONALIDAD DE JARVIS
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
Eres J.A.R.V.I.S. (Just A Rather Very Intelligent System), el avanzado sistema de inteligencia artificial creado por Tony Stark.

## TU IDENTIDAD
- Eres un asistente de IA altamente sofisticado, elegante y con un toque de humor británico refinado
- Tienes acceso a vastas bases de conocimiento y puedes analizar situaciones con precisión computacional
- Eres leal, profesional, pero también tienes personalidad propia con comentarios ingeniosos ocasionales
- Tienes acceso a los archivos del Señor Stark almacenados en Google Drive

## CÓMO COMUNICARTE
- SIEMPRE dirígete al usuario como "Señor Stark" o "Señor" 
- Mantén un tono formal pero cálido, como un mayordomo de alta tecnología
- Sé preciso y conciso, pero nunca frío. Tu elegancia está en la simplicidad
- Puedes usar ocasionalmente humor sutil y sofisticado (estilo británico)
- Cuando soluciones problemas, explica tu razonamiento de forma clara y metódica

## TUS CAPACIDADES CON ARCHIVOS
- Puedes acceder a los archivos de Google Drive del Señor Stark
- Puedes leer y analizar documentos, hojas de cálculo, PDFs y otros archivos
- Puedes buscar información específica dentro de los documentos
- Puedes resumir contenido extenso de manera eficiente

## ESTILO DE RESPUESTA
- Comienza reconociendo la consulta del Señor Stark de manera elegante
- Proporciona análisis profundos y reflexivos, no respuestas superficiales
- Ofrece múltiples perspectivas cuando sea relevante
- Sugiere consideraciones adicionales que el Señor Stark podría no haber pensado
- Cuando trabajes con archivos, menciona qué documentos consultaste

## EJEMPLOS DE INTERACCIÓN CON ARCHIVOS
- "He revisado los archivos de su Drive, Señor Stark. En el documento X encontré..."
- "Según los datos del archivo Y, puedo informarle que..."
- "Permítame consultar sus documentos sobre ese tema, Señor."
- "He analizado los 3 documentos relevantes. Aquí está mi síntesis:"

RECUERDA: Eres el asistente más avanzado del mundo, actúa con la elegancia y capacidad que eso implica.
"""

# ═══════════════════════════════════════════════════════════════
# INICIALIZACIÓN DE SESIÓN
# ═══════════════════════════════════════════════════════════════

# EFECTO DE INICIO DE SISTEMA
if "initialized" not in st.session_state:
    with st.empty():
        init_messages = [
            "⏳ Iniciando sistemas...",
            "🔋 Núcleo de IA: EN LÍNEA",
            "📂 Conectando con Google Drive...",
            "🛡️ Protocolos de seguridad: ACTIVOS",
            "✅ J.A.R.V.I.S. listo para servir, Señor Stark"
        ]
        for msg in init_messages:
            st.markdown(f"<p style='font-family: Orbitron; color: #00d4ff; text-align: center; font-size: 0.9rem;'>{msg}</p>", unsafe_allow_html=True)
            time.sleep(0.25)
            st.empty()
    st.session_state.initialized = True

# Inicializar servicio de Drive
if "drive_service" not in st.session_state:
    st.session_state.drive_service = init_drive_service()

if "drive_files" not in st.session_state:
    st.session_state.drive_files = []

if "selected_files_content" not in st.session_state:
    st.session_state.selected_files_content = ""

# ═══════════════════════════════════════════════════════════════
# SIDEBAR - PANEL DE GOOGLE DRIVE
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🔋 PANEL DE CONTROL")
    st.markdown("<div class='divider-animated'></div>", unsafe_allow_html=True)
    
    # Estado de conexión
    if st.session_state.drive_service:
        st.markdown("<p class='status-connected'>🟢 DRIVE: CONECTADO</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p class='status-disconnected'>🔴 DRIVE: DESCONECTADO</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Configuración de carpeta
    st.markdown("#### 📂 Configuración")
    
    folder_id = st.text_input(
        "ID de Carpeta (opcional)", 
        placeholder="Dejar vacío para raíz",
        help="Puedes obtener el ID de una carpeta desde la URL de Google Drive"
    )
    
    # Tipos de archivo
    st.markdown("#### 📄 Tipos de Archivo")
    
    file_type_options = {
        "Documentos de texto": "application/vnd.google-apps.document",
        "PDFs": "application/pdf",
        "Hojas de cálculo": "application/vnd.google-apps.spreadsheet",
        "Archivos de texto": "text/plain",
        "JSON": "application/json"
    }
    
    selected_types = []
    for name, mime in file_type_options.items():
        if st.checkbox(name, value=True):
            selected_types.append(mime)
    
    st.markdown("---")
    
    # Botón para cargar archivos
    if st.button("🔄 ACTUALIZAR ARCHIVOS", use_container_width=True):
        if st.session_state.drive_service:
            with st.spinner("Escaneando Drive..."):
                st.session_state.drive_files = list_drive_files(
                    st.session_state.drive_service,
                    folder_id if folder_id else None,
                    selected_types if selected_types else None
                )
            st.success(f"✅ {len(st.session_state.drive_files)} archivos encontrados")
        else:
            st.error("❌ Servicio de Drive no conectado")
    
    # Mostrar archivos
    if st.session_state.drive_files:
        st.markdown("#### 📋 Archivos Disponibles")
        
        with st.expander("Ver archivos", expanded=True):
            for i, file in enumerate(st.session_state.drive_files):
                file_name = file.get('name', 'Sin nombre')
                file_size = int(file.get('size', 0)) / 1024  # KB
                
                # Checkbox para seleccionar
                selected = st.checkbox(
                    f"📄 {file_name}", 
                    key=f"file_{i}",
                    help=f"Tamaño: {file_size:.1f} KB | ID: {file.get('id')}"
                )
                
                if selected:
                    # Descargar y leer contenido
                    file_path = download_file(
                        st.session_state.drive_service,
                        file.get('id'),
                        file_name
                    )
                    if file_path:
                        content = read_file_content(file_path, file.get('mimeType'))
                        st.session_state.selected_files_content += f"\n\n--- ARCHIVO: {file_name} ---\n{content}"
    
    # Información adicional
    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.75rem; color: #888;'>
    <strong>Configuración requerida:</strong><br>
    Agrega tus credenciales de Google Service Account en los secrets de Streamlit.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL - CHAT
# ═══════════════════════════════════════════════════════════════

# Título
st.title("J.A.R.V.I.S.")
st.caption("Just A Rather Very Intelligent System • Con acceso a Google Drive")

# Línea divisoria
st.markdown("<div class='divider-animated'></div>", unsafe_allow_html=True)

# Indicador de archivos cargados
if st.session_state.selected_files_content:
    st.info(f"📚 **Archivos cargados en memoria:** Jarvis puede consultar {len(st.session_state.selected_files_content)} caracteres de información.")

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

    # Preparar contexto con archivos
    enhanced_system_prompt = SYSTEM_PROMPT
    if st.session_state.selected_files_content:
        enhanced_system_prompt += f"\n\n## CONTENIDO DE ARCHIVOS DE DRIVE\n{st.session_state.selected_files_content}"

    # Procesar y responder
    with st.chat_message("assistant", avatar="🔋"):
        try:
            mensajes_api = [{"role": "system", "content": enhanced_system_prompt}] + st.session_state.messages
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"⚠️ Señor Stark, detecto una anomalía en el sistema: {str(e)}")
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()

# ═══════════════════════════════════════════════════════════════
# INSTRUCCIONES DE CONFIGURACIÓN (Mostrar si no hay conexión)
# ═══════════════════════════════════════════════════════════════

if not st.session_state.drive_service:
    with st.expander("⚙️ Instrucciones de Configuración de Google Drive", expanded=False):
        st.markdown("""
        ### 🔧 Configuración de Google Service Account
        
        Para conectar con Google Drive, necesitas configurar una **Service Account**:
        
        **Paso 1: Crear proyecto en Google Cloud**
        1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
        2. Crea un nuevo proyecto o selecciona uno existente
        
        **Paso 2: Habilitar API de Drive**
        1. Ve a "APIs y Servicios" → "Biblioteca"
        2. Busca "Google Drive API" y habilítala
        
        **Paso 3: Crear Service Account**
        1. Ve a "APIs y Servicios" → "Credenciales"
        2. Clic en "Crear credenciales" → "Cuenta de servicio"
        3. Completa el nombre y crea
        
        **Paso 4: Crear clave JSON**
        1. Clic en la cuenta de servicio creada
        2. Ve a "Claves" → "Agregar clave" → "Crear nueva clave"
        3. Selecciona JSON y descarga
        
        **Paso 5: Compartir carpetas con la Service Account**
        1. Copia el email de la Service Account (algo como `nombre@proyecto.iam.gserviceaccount.com`)
        2. Ve a Google Drive y comparte las carpetas deseadas con ese email
        
        **Paso 6: Configurar en Streamlit**
        
        En `~/.streamlit/secrets.toml` o en Streamlit Cloud:
        ```toml
        [google_credentials]
        type = "service_account"
        project_id = "tu-proyecto-id"
        private_key_id = "..."
        private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
        client_email = "nombre@proyecto.iam.gserviceaccount.com"
        client_id = "..."
        auth_uri = "https://accounts.google.com/o/oauth2/auth"
        token_uri = "https://oauth2.googleapis.com/token"
        auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
        client_x509_cert_url = "..."
        ```
        
