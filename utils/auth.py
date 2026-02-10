"""
Utilidades de autenticación con Supabase
"""

import streamlit as st
from supabase import create_client, Client
import os

def init_supabase() -> Client:
    """
    Inicializar cliente de Supabase
    
    Returns:
        Client: Cliente de Supabase configurado
    """
    # Para Streamlit Cloud, usar secrets
    # Para desarrollo local, usar variables de entorno
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
    except:
        # Fallback para desarrollo local
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        st.error("""
        ⚠️ **Configuración requerida**
        
        Por favor configura las credenciales de Supabase:
        
        1. Crea un proyecto en https://supabase.com
        2. Copia tu URL y API Key
        3. En Streamlit Cloud: Settings → Secrets
        4. Pega:
```toml
        SUPABASE_URL = "tu-url-de-supabase"
        SUPABASE_KEY = "tu-key-de-supabase"
```
        """)
        st.stop()
    
    return create_client(supabase_url, supabase_key)

def login_user(supabase: Client, email: str, password: str) -> dict:
    """
    Iniciar sesión de usuario
    
    Args:
        supabase: Cliente de Supabase
        email: Email del usuario
        password: Contraseña
        
    Returns:
        dict: Datos del usuario si tiene éxito, None si falla
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            # IMPORTANTE: Configurar el token de sesión en el cliente
            supabase.auth.set_session(response.session.access_token, response.session.refresh_token)
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token
            }
        return None
    except Exception as e:
        st.error(f"Error al iniciar sesión: {str(e)}")
        return None

def register_user(supabase: Client, email: str, password: str) -> dict:
    """
    Registrar nuevo usuario
    
    Args:
        supabase: Cliente de Supabase
        email: Email del usuario
        password: Contraseña
        
    Returns:
        dict: Datos del usuario si tiene éxito, None si falla
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            # Configurar el token de sesión
            supabase.auth.set_session(response.session.access_token, response.session.refresh_token)
            
            # Crear perfil de inversor por defecto
            create_default_profile(supabase, response.user.id)
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token
            }
        return None
    except Exception as e:
        st.error(f"Error al registrar usuario: {str(e)}")
        return None
        
def logout_user():
    """Cerrar sesión del usuario"""
    st.session_state.user = None
    st.session_state.current_page = "dashboard"
    if 'portfolio_data' in st.session_state:
        del st.session_state.portfolio_data

def create_default_profile(supabase: Client, user_id: str):
    """
    Crear perfil de inversor por defecto para nuevo usuario
    
    Args:
        supabase: Cliente de Supabase
        user_id: ID del usuario
    """
    try:
        supabase.table('investor_profiles').insert({
            'user_id': user_id,
            'investment_horizon': 'medio_plazo',
            'risk_tolerance': 'moderado',
            'investment_goal': 'capitalizacion'
        }).execute()
    except Exception as e:
        # No mostrar error al usuario, el perfil se puede crear después
        print(f"Error creando perfil por defecto: {str(e)}")
