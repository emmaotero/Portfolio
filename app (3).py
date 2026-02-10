"""
Portfolio Manager - Aplicación Principal para Google Colab
"""

import streamlit as st
from supabase import create_client, Client
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import os

# Configuración de página
st.set_page_config(
    page_title="Portfolio Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_supabase() -> Client:
    """
    Inicializar cliente de Supabase
    
    Returns:
        Client: Cliente de Supabase configurado
    """
    # Para desarrollo local, usar variables de entorno
    # Para producción en Streamlit Cloud, usar secrets
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
        
        Por favor configura las credenciales de Supabase en Streamlit Cloud Settings → Secrets
        """)
        st.stop()
    
    return create_client(supabase_url, supabase_key)

# ============================================================================
# ESTILOS CSS
# ============================================================================

def apply_custom_styles():
    """Aplicar estilos CSS personalizados"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #141821;
        --bg-card: #1a1f2e;
        --accent-primary: #00d4aa;
        --accent-secondary: #7c3aed;
        --text-primary: #e8eaed;
        --success: #10b981;
        --danger: #ef4444;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f1419 100%);
        font-family: 'Sora', sans-serif;
        color: var(--text-primary);
    }
    
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
    }
    
    .metric-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #2d3748;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 8px 32px rgba(0, 212, 170, 0.15);
        transform: translateY(-4px);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .metric-change.positive { color: var(--success); }
    .metric-change.negative { color: var(--danger); }
    
    h1 {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# AUTENTICACIÓN
# ============================================================================

def init_supabase():
    """Inicializar cliente Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("⚠️ Configura las credenciales de Supabase en el notebook")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def login_user(supabase, email, password):
    """Iniciar sesión"""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            return {"id": response.user.id, "email": response.user.email}
    except:
        return None
    return None

def register_user(supabase, email, password):
    """Registrar usuario"""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            return {"id": response.user.id, "email": response.user.email}
    except:
        return None
    return None

# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================

def get_user_positions(supabase, user_id):
    """Obtener posiciones del usuario"""
    try:
        response = supabase.table('positions').select('*').eq('user_id', user_id).execute()
        return response.data if response.data else []
    except:
        return []

def add_position(supabase, user_id, ticker, quantity, price, date_str):
    """Agregar posición"""
    try:
        data = {
            'user_id': user_id,
            'ticker': ticker.upper(),
            'quantity': quantity,
            'purchase_price': price,
            'purchase_date': date_str
        }
        supabase.table('positions').insert(data).execute()
        return True
    except:
        return False

def delete_position(supabase, position_id):
    """Eliminar posición"""
    try:
        supabase.table('positions').delete().eq('id', position_id).execute()
        return True
    except:
        return False

# ============================================================================
# DATOS DE MERCADO
# ============================================================================

@st.cache_data(ttl=300)
def get_current_price(ticker):
    """Obtener precio actual"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_historical_data(ticker, period="1y"):
    """Obtener datos históricos"""
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period=period)
    except:
        return pd.DataFrame()

def calculate_rsi(data, period=14):
    """Calcular RSI"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    """Calcular MACD"""
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal, macd - signal

def calculate_sma(data, period):
    """Calcular SMA"""
    return data['Close'].rolling(window=period).mean()

def calculate_bollinger_bands(data, period=20):
    """Calcular Bandas de Bollinger"""
    middle = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    upper = middle + (std * 2)
    lower = middle - (std * 2)
    return upper, middle, lower

# ============================================================================
# INTERFAZ DE USUARIO
# ============================================================================

def show_auth_page(supabase):
    """Página de autenticación"""
    st.markdown("<h1 style='text-align: center;'>📊 Portfolio Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af;'>Gestiona tu portfolio de inversiones</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                user = login_user(supabase, email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    
    with tab2:
        with st.form("register"):
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Contraseña", type="password", key="reg_pass")
            confirm = st.text_input("Confirmar", type="password")
            if st.form_submit_button("Registrarse", use_container_width=True):
                if password == confirm and len(password) >= 6:
                    user = register_user(supabase, email, password)
                    if user:
                        st.success("Cuenta creada! Iniciando sesión...")
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Error al crear cuenta")
                else:
                    st.warning("Las contraseñas no coinciden o son muy cortas")

def show_dashboard(supabase, user):
    """Dashboard principal"""
    st.markdown("# 📊 Dashboard")
    
    positions = get_user_positions(supabase, user['id'])
    
    if not positions:
        st.info("No tienes posiciones. Ve a 'Mi Portfolio' para agregar una.")
        return
    
    # Obtener precios actuales
    with st.spinner("Actualizando precios..."):
        current_prices = {}
        for pos in positions:
            price = get_current_price(pos['ticker'])
            current_prices[pos['ticker']] = price if price else pos['purchase_price']
    
    # Calcular métricas
    total_invested = sum(p['quantity'] * p['purchase_price'] for p in positions)
    total_value = sum(p['quantity'] * current_prices[p['ticker']] for p in positions)
    total_pnl = total_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Capital Invertido</div>
            <div class="metric-value">${total_invested:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Valor Actual</div>
            <div class="metric-value">${total_value:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pnl_class = "positive" if total_pnl >= 0 else "negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">P&L</div>
            <div class="metric-value">${total_pnl:,.2f}</div>
            <div class="metric-change {pnl_class}">{total_pnl_pct:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Posiciones</div>
            <div class="metric-value">{len(positions)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabla de posiciones
    st.markdown("### 💼 Mis Posiciones")
    
    data = []
    for p in positions:
        current_price = current_prices[p['ticker']]
        value = p['quantity'] * current_price
        invested = p['quantity'] * p['purchase_price']
        pnl = value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0
        
        data.append({
            'Ticker': p['ticker'],
            'Cantidad': f"{p['quantity']:.4f}",
            'Precio Compra': f"${p['purchase_price']:.2f}",
            'Precio Actual': f"${current_price:.2f}",
            'Valor': f"${value:,.2f}",
            'P&L': f"${pnl:,.2f}",
            'P&L %': f"{pnl_pct:+.2f}%"
        })
    
    st.dataframe(pd.DataFrame(data), use_container_width=True)

def show_portfolio(supabase, user):
    """Gestión de portfolio"""
    st.markdown("# 💼 Mi Portfolio")
    
    tab1, tab2 = st.tabs(["Ver Posiciones", "Agregar Posición"])
    
    with tab1:
        positions = get_user_positions(supabase, user['id'])
        
        if not positions:
            st.info("No tienes posiciones")
        else:
            for pos in positions:
                with st.expander(f"**{pos['ticker']}** - {pos['quantity']} acciones"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Precio compra:** ${pos['purchase_price']:.2f}")
                        st.write(f"**Fecha:** {pos['purchase_date']}")
                    with col2:
                        if st.button("🗑️ Eliminar", key=f"del_{pos['id']}"):
                            if delete_position(supabase, pos['id']):
                                st.success("Eliminado")
                                st.rerun()
    
    with tab2:
        with st.form("add_position"):
            col1, col2 = st.columns(2)
            
            with col1:
                ticker = st.text_input("Ticker", placeholder="AAPL").upper()
                quantity = st.number_input("Cantidad", min_value=0.0001, step=0.01, format="%.4f")
            
            with col2:
                price = st.number_input("Precio de Compra", min_value=0.01, step=0.01)
                purchase_date = st.date_input("Fecha", value=date.today())
            
            if st.form_submit_button("Agregar", use_container_width=True):
                if ticker and quantity > 0 and price > 0:
                    if add_position(supabase, user['id'], ticker, quantity, price, str(purchase_date)):
                        st.success(f"✅ {ticker} agregado")
                        st.rerun()
                else:
                    st.error("Completa todos los campos")

def show_analysis(supabase, user):
    """Análisis técnico"""
    st.markdown("# 📈 Análisis Técnico")
    
    positions = get_user_positions(supabase, user['id'])
    
    if not positions:
        st.info("No tienes posiciones para analizar")
        return
    
    tickers = sorted(list(set([p['ticker'] for p in positions])))
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.selectbox("Selecciona ticker", tickers)
    with col2:
        period = st.selectbox("Período", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
    
    if not ticker:
        return
    
    with st.spinner("Calculando indicadores..."):
        data = get_historical_data(ticker, period)
        
        if data.empty:
            st.error("No se pudieron obtener los datos")
            return
        
        # Calcular indicadores
        rsi = calculate_rsi(data)
        macd, signal, hist = calculate_macd(data)
        sma_50 = calculate_sma(data, 50)
        sma_200 = calculate_sma(data, 200)
        upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(data)
        
        current_price = data['Close'].iloc[-1]
        
        # Métricas de indicadores
        st.markdown("### 📊 Indicadores Actuales")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Precio", f"${current_price:.2f}")
        with col2:
            st.metric("RSI", f"{rsi.iloc[-1]:.1f}")
        with col3:
            st.metric("MACD", f"{macd.iloc[-1]:.2f}")
        with col4:
            st.metric("SMA 50", f"${sma_50.iloc[-1]:.2f}")
        with col5:
            st.metric("SMA 200", f"${sma_200.iloc[-1]:.2f}")
        
        st.markdown("---")
        
        # Gráfico de precio con Bollinger Bands
        st.markdown("### 📈 Precio y Bandas de Bollinger")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=data.index, y=upper_bb, name='BB Superior',
                                line=dict(color='rgba(124, 58, 237, 0.3)', dash='dash')))
        fig.add_trace(go.Scatter(x=data.index, y=lower_bb, name='BB Inferior',
                                line=dict(color='rgba(124, 58, 237, 0.3)', dash='dash'),
                                fill='tonexty', fillcolor='rgba(124, 58, 237, 0.1)'))
        fig.add_trace(go.Scatter(x=data.index, y=sma_50, name='SMA 50',
                                line=dict(color='#f59e0b', width=2)))
        fig.add_trace(go.Scatter(x=data.index, y=sma_200, name='SMA 200',
                                line=dict(color='#ef4444', width=2)))
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Precio',
                                line=dict(color='#00d4aa', width=3)))
        
        fig.update_layout(height=500, hovermode='x unified',
                         paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(26, 31, 46, 0.5)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de RSI
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 RSI")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI',
                                        line=dict(color='#00d4aa', width=2)))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#10b981")
            fig_rsi.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)',
                                 plot_bgcolor='rgba(26, 31, 46, 0.5)')
            st.plotly_chart(fig_rsi, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 MACD")
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=data.index, y=macd, name='MACD',
                                         line=dict(color='#00d4aa', width=2)))
            fig_macd.add_trace(go.Scatter(x=data.index, y=signal, name='Signal',
                                         line=dict(color='#ef4444', width=2)))
            fig_macd.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(26, 31, 46, 0.5)')
            st.plotly_chart(fig_macd, use_container_width=True)

# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    apply_custom_styles()
    
    supabase = init_supabase()
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_auth_page(supabase)
    else:
        # Sidebar
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.user['email']}")
            st.markdown("---")
            
            if 'page' not in st.session_state:
                st.session_state.page = 'dashboard'
            
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page = 'dashboard'
            if st.button("💼 Mi Portfolio", use_container_width=True):
                st.session_state.page = 'portfolio'
            if st.button("📈 Análisis Técnico", use_container_width=True):
                st.session_state.page = 'analysis'
            
            st.markdown("---")
            
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        
        # Contenido principal
        if st.session_state.page == 'dashboard':
            show_dashboard(supabase, st.session_state.user)
        elif st.session_state.page == 'portfolio':
            show_portfolio(supabase, st.session_state.user)
        elif st.session_state.page == 'analysis':
            show_analysis(supabase, st.session_state.user)

if __name__ == "__main__":
    main()
