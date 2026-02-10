"""
Utilidades de autenticación con Supabase
"""

import streamlit as st
from supabase import create_client, Client
import os

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
        
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email
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
        dict: Datos del usuario si tiene éxito, None si falló
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Crear perfil de inversor por defecto
            create_default_profile(supabase, response.user.id)
            
            return {
                "id": response.user.id,
                "email": response.user.email
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
        print(f"Error creando perfil por defecto: {str(e)}")
