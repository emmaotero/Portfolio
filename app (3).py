"""
Portfolio Manager - Main Application
Multi-user portfolio management system with authentication
"""

import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime

# Configuración de página - debe ser lo primero
st.set_page_config(
    page_title="Portfolio Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar utilidades después de set_page_config
from utils.auth import init_supabase, login_user, register_user, logout_user
from utils.styles import apply_custom_styles
from pages import dashboard, portfolio, analysis, profile

# Inicializar Supabase
if 'user' in st.session_state and st.session_state.user and 'access_token' in st.session_state.user:
    # Recrear cliente con el token del usuario
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase = create_client(
        supabase_url, 
        st.secrets["SUPABASE_KEY"],
        options={
            "headers": {
                "Authorization": f"Bearer {st.session_state.user['access_token']}"
            }
        }
    )
else:
    supabase = init_supabase()

# Aplicar estilos personalizados
apply_custom_styles()

def main():
    """Función principal de la aplicación"""
    
    # Inicializar estado de sesión
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Si el usuario no está autenticado, mostrar login/registro
    if st.session_state.user is None:
        show_auth_page()
    else:
        show_app()

def show_auth_page():
    """Página de autenticación (login/registro)"""
    
    # Header
    st.markdown("""
        <div class="auth-header">
            <h1>📊 Portfolio Manager</h1>
            <p>Gestiona tu portfolio de inversiones de manera profesional</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Crear dos columnas para centrar el contenido
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab1:
            st.markdown("### Bienvenido de vuelta")
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="tu@email.com")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                
                if submit:
                    if email and password:
                        user = login_user(supabase, email, password)
                        if user:
                            st.session_state.user = user
                            st.rerun()
                        else:
                            st.error("❌ Email o contraseña incorrectos")
                    else:
                        st.warning("⚠️ Por favor completa todos los campos")
        
        with tab2:
            st.markdown("### Crear cuenta nueva")
            with st.form("register_form"):
                new_email = st.text_input("Email", placeholder="tu@email.com", key="reg_email")
                new_password = st.text_input("Contraseña", type="password", 
                                            placeholder="Mínimo 6 caracteres", key="reg_pass")
                confirm_password = st.text_input("Confirmar Contraseña", type="password",
                                                placeholder="••••••••", key="reg_confirm")
                submit = st.form_submit_button("Registrarse", use_container_width=True)
                
                if submit:
                    if new_email and new_password and confirm_password:
                        if new_password == confirm_password:
                            if len(new_password) >= 6:
                                user = register_user(supabase, new_email, new_password)
                                if user:
                                    st.success("✅ Cuenta creada exitosamente! Iniciando sesión...")
                                    st.session_state.user = user
                                    st.rerun()
                                else:
                                    st.error("❌ Error al crear la cuenta. El email puede estar en uso.")
                            else:
                                st.warning("⚠️ La contraseña debe tener al menos 6 caracteres")
                        else:
                            st.warning("⚠️ Las contraseñas no coinciden")
                    else:
                        st.warning("⚠️ Por favor completa todos los campos")

def show_app():
    """Mostrar la aplicación principal cuando el usuario está autenticado"""
    
    # Sidebar con navegación
    with st.sidebar:
        st.markdown(f"""
            <div class="user-info">
                <div class="user-avatar">👤</div>
                <div class="user-details">
                    <div class="user-email">{st.session_state.user.get('email', 'Usuario')}</div>
                    <div class="user-role">Inversor</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navegación
        st.markdown("### 📍 Navegación")
        
        pages = {
            "📊 Dashboard": "dashboard",
            "💼 Mi Portfolio": "portfolio",
            "📈 Análisis Técnico": "analysis",
            "👤 Perfil del Inversor": "profile"
        }
        
        # Inicializar página actual
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        for page_name, page_key in pages.items():
            if st.button(page_name, key=f"nav_{page_key}", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Botón de logout
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()
        
        # Footer
        st.markdown("""
            <div class="sidebar-footer">
                <p>Portfolio Manager v1.0</p>
                <p style="font-size: 0.7rem; opacity: 0.5;">Datos de mercado en tiempo real</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Contenido principal según la página seleccionada
    if st.session_state.current_page == "dashboard":
        dashboard.show(supabase, st.session_state.user)
    elif st.session_state.current_page == "portfolio":
        portfolio.show(supabase, st.session_state.user)
    elif st.session_state.current_page == "analysis":
        analysis.show(supabase, st.session_state.user)
    elif st.session_state.current_page == "profile":
        profile.show(supabase, st.session_state.user)

if __name__ == "__main__":
    main()
