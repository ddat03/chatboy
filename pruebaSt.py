import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# Cargar datos
@st.cache_data
def load_data():
    try:
        income_spending = pd.read_csv('datos_chatboy.csv')
        return income_spending.to_string()
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo datos_chatboy.csv")
        return "Datos no disponibles"

df_string = load_data()

# Función para validar token
def validate_token(token):
    if token and token.startswith('sk-'):
        return True
    return False

# Función para obtener respuesta de OpenAI
def get_bot_response(question, api_key):
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": f"Eres un analista de datos. Necesito que contestes solo preguntas relacionados a los siguientes datos, caso contrario contesta esto: Solo respondo preguntas relacionadas a los datos:\n{df_string}"
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Inicializar session state
if "past" not in st.session_state:
    st.session_state["past"] = []

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "api_token" not in st.session_state:
    st.session_state["api_token"] = ""

if "token_valid" not in st.session_state:
    st.session_state["token_valid"] = False

# Función para manejar cambio de token
def on_token_change():
    token = st.session_state.token_input
    st.session_state.api_token = token
    st.session_state.token_valid = validate_token(token)
    if st.session_state.token_valid:
        os.environ['OPENAI_API_KEY'] = token

# Función para manejar input de preguntas
def on_input_change():
    user_input = st.session_state.question
    if user_input and st.session_state.token_valid:
        # Agregar pregunta del usuario
        st.session_state.past.append(user_input)
        
        # Obtener respuesta del bot
        with st.spinner("Analizando..."):
            bot_response = get_bot_response(user_input, st.session_state.api_token)
            st.session_state.generated.append(bot_response)
        
        # Limpiar el input
        st.session_state.question = ""

# Función para limpiar chat
def on_btn_click():
    st.session_state.past.clear()
    st.session_state.generated.clear()

# Título y descripción
st.title("📊 Chatboy Diego Aleman")
st.caption("Realice preguntas relacionadas a los datos")

# Sidebar con configuración del token
with st.sidebar:
    st.header("🔑 Configuración")
    
    # Input para el token
    st.text_input(
        "Ingresa tu OpenAI API Token:", 
        type="password",  # Oculta el texto como contraseña
        on_change=on_token_change, 
        key="token_input",
        placeholder="sk-proj-..."
    )
    
    # Mostrar estado del token
    if st.session_state.token_valid:
        st.success("✅ Token válido")
    elif st.session_state.api_token:
        st.error("❌ Token inválido")
    else:
        st.warning("⚠️ Ingresa tu token para comenzar")
    
    st.markdown("---")
    
    st.header("📋 Información")
    st.write(f"Preguntas realizadas: {len(st.session_state.past)}")
    
    with st.expander("👀 Ver datos"):
        try:
            df = pd.read_csv('datos_chatboy.csv')
            st.dataframe(df.head())
        except:
            st.write("No se pudieron cargar los datos para vista previa")
    
    st.markdown("---")
    
    # Instrucciones
    st.markdown("""
    ### 💡 Cómo obtener tu token:
    1. Ve a [OpenAI API](https://platform.openai.com/api-keys)
    2. Inicia sesión en tu cuenta
    3. Crea una nueva API key
    4. Cópiala y pégala arriba
    
    ### 🛡️ Seguridad:
    - Tu token no se guarda permanentemente
    - Solo se usa durante la sesión actual
    """)

# Verificar si el token está configurado antes de mostrar la interfaz de chat
if not st.session_state.token_valid:
    st.info("🔑 Por favor, configura tu token de OpenAI en la barra lateral para comenzar.")
else:
    # Interfaz principal (solo si hay token válido)
    with st.container():
        st.text_input("Haga una pregunta:", on_change=on_input_change, key="question")
        st.button("🗑️ Limpiar Chat", on_click=on_btn_click)

    # Mostrar conversación
    if st.session_state["generated"]:
        with st.container():
            for i in range(len(st.session_state["generated"])):
                # Mostrar mensaje del usuario
                if i < len(st.session_state["past"]):
                    st.markdown(f"""
                    <div style="background-color: #e8f4fd; color: black; padding: 10px; border-radius: 10px; margin: 5px 0;">
                        <strong>🧑 Tú:</strong> {st.session_state["past"][i]}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Mostrar respuesta del bot
                st.markdown(f"""
                <div style="background-color: #e8f5e8; color: black; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>🤖 Bot:</strong> {st.session_state["generated"][i]}
                </div>
                """, unsafe_allow_html=True)
