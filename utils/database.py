"""
Utilidades para interactuar con la base de datos Supabase
"""

from supabase import Client
import pandas as pd
from datetime import datetime
import streamlit as st

def get_user_positions(supabase: Client, user_id: str) -> list:
    """
    Obtener todas las posiciones del usuario
    
    Args:
        supabase: Cliente de Supabase
        user_id: ID del usuario
        
    Returns:
        list: Lista de posiciones
    """
    try:
        response = supabase.table('positions').select('*').eq('user_id', user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error obteniendo posiciones: {str(e)}")
        return []

def add_position(supabase: Client, user_id: str, ticker: str, quantity: float, 
                purchase_price: float, purchase_date: str) -> bool:
    """
    Agregar nueva posición al portfolio
    """
    
    # DEBUG: Mostrar user_id
    st.warning(f"🔍 DEBUG: user_id desde la app = {user_id}")
    
    try:
        data = {
            'user_id': user_id,
            'ticker': ticker.upper(),
            'quantity': quantity,
            'purchase_price': purchase_price,
            'purchase_date': purchase_date,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('positions').insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error agregando posición: {str(e)}")
        return False

def update_position(supabase: Client, position_id: int, quantity: float = None, 
                   purchase_price: float = None, purchase_date: str = None) -> bool:
    """
    Actualizar posición existente
    
    Args:
        supabase: Cliente de Supabase
        position_id: ID de la posición
        quantity: Nueva cantidad (opcional)
        purchase_price: Nuevo precio (opcional)
        purchase_date: Nueva fecha (opcional)
        
    Returns:
        bool: True si tuvo éxito, False si falló
    """
    try:
        data = {}
        if quantity is not None:
            data['quantity'] = quantity
        if purchase_price is not None:
            data['purchase_price'] = purchase_price
        if purchase_date is not None:
            data['purchase_date'] = purchase_date
        
        if data:
            data['updated_at'] = datetime.now().isoformat()
            supabase.table('positions').update(data).eq('id', position_id).execute()
        
        return True
    except Exception as e:
        st.error(f"Error actualizando posición: {str(e)}")
        return False

def delete_position(supabase: Client, position_id: int) -> bool:
    """
    Eliminar posición
    
    Args:
        supabase: Cliente de Supabase
        position_id: ID de la posición
        
    Returns:
        bool: True si tuvo éxito, False si falló
    """
    try:
        supabase.table('positions').delete().eq('id', position_id).execute()
        return True
    except Exception as e:
        st.error(f"Error eliminando posición: {str(e)}")
        return False

def get_investor_profile(supabase: Client, user_id: str) -> dict:
    """
    Obtener perfil del inversor
    
    Args:
        supabase: Cliente de Supabase
        user_id: ID del usuario
        
    Returns:
        dict: Datos del perfil o None si no existe
    """
    try:
        response = supabase.table('investor_profiles').select('*').eq('user_id', user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error obteniendo perfil: {str(e)}")
        return None

def update_investor_profile(supabase: Client, user_id: str, investment_horizon: str = None,
                           risk_tolerance: str = None, investment_goal: str = None) -> bool:
    """
    Actualizar perfil del inversor
    
    Args:
        supabase: Cliente de Supabase
        user_id: ID del usuario
        investment_horizon: Horizonte de inversión
        risk_tolerance: Tolerancia al riesgo
        investment_goal: Objetivo de inversión
        
    Returns:
        bool: True si tuvo éxito, False si falló
    """
    try:
        existing = get_investor_profile(supabase, user_id)
        
        data = {}
        if investment_horizon is not None:
            data['investment_horizon'] = investment_horizon
        if risk_tolerance is not None:
            data['risk_tolerance'] = risk_tolerance
        if investment_goal is not None:
            data['investment_goal'] = investment_goal
        
        if data:
            data['updated_at'] = datetime.now().isoformat()
            
            if existing:
                supabase.table('investor_profiles').update(data).eq('user_id', user_id).execute()
            else:
                data['user_id'] = user_id
                data['created_at'] = datetime.now().isoformat()
                supabase.table('investor_profiles').insert(data).execute()
        
        return True
    except Exception as e:
        st.error(f"Error actualizando perfil: {str(e)}")
        return False

def calculate_portfolio_metrics(positions: list, current_prices: dict) -> dict:
    """
    Calcular métricas del portfolio (todo en USD)
    
    Args:
        positions: Lista de posiciones
        current_prices: Diccionario con info de precios {ticker: price_info}
        
    Returns:
        dict: Métricas calculadas en USD
    """
    if not positions:
        return {
            'total_invested': 0,
            'total_value': 0,
            'total_pnl': 0,
            'total_pnl_pct': 0,
            'positions_detail': []
        }
    
    total_invested = 0
    total_value = 0
    positions_detail = []
    
    for position in positions:
        ticker = position['ticker']
        quantity = float(position['quantity'])
        purchase_price = float(position['purchase_price'])
        
        # Detectar moneda del ticker
        currency = detect_currency(ticker)
        
        # Convertir precio de compra a USD
        purchase_price_usd = convert_to_usd(purchase_price, currency)
        
        # Calcular inversión en USD
        invested = quantity * purchase_price_usd
        
        # Obtener precio actual
        price_info = current_prices.get(ticker)
        if price_info:
            current_price = price_info['price']
            current_price_usd = price_info['price_usd']
        else:
            current_price = purchase_price
            current_price_usd = purchase_price_usd
        
        current_value = quantity * current_price_usd
        pnl = current_value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0
        
        total_invested += invested
        total_value += current_value
        
        positions_detail.append({
            'id': position['id'],
            'ticker': ticker,
            'quantity': quantity,
            'purchase_price': purchase_price,
            'purchase_price_usd': purchase_price_usd,
            'current_price': current_price,
            'current_price_usd': current_price_usd,
            'currency': currency,
            'invested': invested,
            'current_value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'purchase_date': position.get('purchase_date', 'N/A')
        })
    
    total_pnl = total_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    # Calcular distribución
    for detail in positions_detail:
        detail['allocation'] = (detail['current_value'] / total_value * 100) if total_value > 0 else 0
    
    return {
        'total_invested': total_invested,
        'total_value': total_value,
        'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct,
        'positions_detail': positions_detail
    }
