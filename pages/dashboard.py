"""
Dashboard - Vista general del portfolio
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.database import get_user_positions, calculate_portfolio_metrics
from utils.market_data import get_current_price
import pandas as pd

def show(supabase, user):
    """Mostrar dashboard principal"""
    
    st.markdown("# 📊 Dashboard")
    st.markdown("Vista general de tu portfolio de inversiones")
    
    # Obtener posiciones del usuario
    positions = get_user_positions(supabase, user['id'])
    
    if not positions:
        show_empty_state()
        return
    
    # Obtener precios actuales
    with st.spinner("Actualizando precios..."):
    current_prices = {}
    for position in positions:
        ticker = position['ticker']
        price_info = get_current_price(ticker)
        if price_info:
            current_prices[ticker] = price_info
        else:
            # Fallback
            currency = detect_currency(ticker)
            current_prices[ticker] = {
                'price': position['purchase_price'],
                'currency': currency,
                'price_usd': convert_to_usd(position['purchase_price'], currency)
            }
    
    # Calcular métricas
    metrics = calculate_portfolio_metrics(positions, current_prices)
    
    # Mostrar métricas principales
    show_main_metrics(metrics)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        show_allocation_chart(metrics['positions_detail'])
    
    with col2:
        show_performance_chart(metrics['positions_detail'])
    
    st.markdown("---")
    
    # Tabla de posiciones resumida
    show_positions_summary(metrics['positions_detail'])

def show_empty_state():
    """Mostrar estado vacío cuando no hay posiciones"""
    st.info("""
    👋 **¡Bienvenido a Portfolio Manager!**
    
    Aún no tienes posiciones en tu portfolio. Ve a la sección **Mi Portfolio** para agregar tu primera inversión.
    """)

def show_main_metrics(metrics):
    """Mostrar métricas principales del portfolio"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Capital Invertido</div>
            <div class="metric-value">${metrics['total_invested']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Valor Actual</div>
            <div class="metric-value">${metrics['total_value']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pnl_class = "positive" if metrics['total_pnl'] >= 0 else "negative"
        pnl_symbol = "▲" if metrics['total_pnl'] >= 0 else "▼"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ganancia/Pérdida</div>
            <div class="metric-value">${metrics['total_pnl']:,.2f}</div>
            <div class="metric-change {pnl_class}">{pnl_symbol} {abs(metrics['total_pnl_pct']):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        num_positions = len(metrics['positions_detail'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Posiciones Activas</div>
            <div class="metric-value">{num_positions}</div>
        </div>
        """, unsafe_allow_html=True)

def show_allocation_chart(positions_detail):
    """Mostrar gráfico de distribución del portfolio"""
    
    st.markdown("### 📊 Distribución del Portfolio")
    
    # Preparar datos
    tickers = [p['ticker'] for p in positions_detail]
    values = [p['current_value'] for p in positions_detail]
    
    # Crear gráfico de pie
    fig = go.Figure(data=[go.Pie(
        labels=tickers,
        values=values,
        hole=0.4,
        marker=dict(
            colors=px.colors.sequential.Teal,
            line=dict(color='#1a1f2e', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.2f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Sora'),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_performance_chart(positions_detail):
    """Mostrar gráfico de rendimiento por activo"""
    
    st.markdown("### 📈 Rendimiento por Activo")
    
    # Preparar datos
    df = pd.DataFrame(positions_detail)
    df = df.sort_values('pnl_pct', ascending=True)
    
    # Crear gráfico de barras
    colors = ['#ef4444' if x < 0 else '#10b981' for x in df['pnl_pct']]
    
    fig = go.Figure(data=[go.Bar(
        x=df['pnl_pct'],
        y=df['ticker'],
        orientation='h',
        marker=dict(color=colors),
        text=df['pnl_pct'].apply(lambda x: f'{x:.2f}%'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Rendimiento: %{x:.2f}%<extra></extra>'
    )])
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Sora'),
        xaxis=dict(
            title='Rendimiento (%)',
            gridcolor='#2d3748',
            showgrid=True
        ),
        yaxis=dict(
            title='',
            gridcolor='#2d3748'
        ),
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_positions_summary(positions_detail):
    """Mostrar tabla resumida de posiciones"""
    
    st.markdown("### 💼 Resumen de Posiciones")
    
    # Preparar DataFrame
    df = pd.DataFrame(positions_detail)
    
    # Formatear columnas para mostrar
    display_df = pd.DataFrame({
    'Ticker': df['ticker'],
    'Moneda': df['currency'],
    'Cantidad': df['quantity'].apply(lambda x: f"{x:.4f}"),
    'Precio Compra': df.apply(lambda x: f"${x['purchase_price']:.2f} {x['currency']}", axis=1),
    'Precio Actual': df.apply(lambda x: f"${x['current_price']:.2f} {x['currency']}", axis=1),
    'Valor (USD)': df['current_value'].apply(lambda x: f"${x:,.2f}"),
    'P&L': df['pnl'].apply(lambda x: f"${x:,.2f}"),
    'P&L %': df['pnl_pct'].apply(lambda x: f"{x:.2f}%"),
    'Distribución': df['allocation'].apply(lambda x: f"{x:.1f}%")
})
    })
    
    # Aplicar estilo
    def color_pnl(val):
        """Colorear valores de P&L"""
        if isinstance(val, str) and '$' in val:
            num = float(val.replace('$', '').replace(',', ''))
            if num < 0:
                return 'color: #ef4444'
            elif num > 0:
                return 'color: #10b981'
        return ''
    
    styled_df = display_df.style.applymap(
        color_pnl, 
        subset=['P&L', 'P&L %']
    )
    
    st.dataframe(styled_df, use_container_width=True, height=400)
