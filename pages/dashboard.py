"""
Dashboard - Vista general del portfolio
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.database import get_user_positions, calculate_portfolio_metrics
from utils.market_data import get_current_price, detect_currency, convert_to_usd
import pandas as pd

def show(supabase, user):
    """Mostrar dashboard principal"""
    
    st.markdown("# 📊 Dashboard")
    
    # Selector de moneda
    col_title, col_currency = st.columns([3, 1])
    
    with col_title:
        st.markdown("Vista general de tu portfolio de inversiones")
    
    with col_currency:
        currency_display = st.selectbox(
            "Moneda:",
            ["USD", "ARS"],
            index=0,
            key="currency_selector"
        )
    
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
                currency = detect_currency(ticker)
                current_prices[ticker] = {
                    'price': position['purchase_price'],
                    'currency': currency,
                    'price_usd': convert_to_usd(position['purchase_price'], currency)
                }
    
    # Calcular métricas
    metrics = calculate_portfolio_metrics(positions, current_prices)
    
    # Convertir a ARS si es necesario
    from utils.market_data import get_usd_ars_rate
    usd_ars = get_usd_ars_rate()
    
    if currency_display == "ARS":
        metrics = convert_metrics_to_ars(metrics, usd_ars)
    
    # Mostrar métricas principales
    show_main_metrics(metrics, currency_display)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        show_allocation_chart(metrics['positions_detail'])
    
    with col2:
        show_performance_chart(metrics['positions_detail'])
    
    st.markdown("---")
    
    # Tabla de posiciones resumida
    show_positions_summary(metrics['positions_detail'], currency_display)

def show_empty_state():
    """Mostrar estado vacío cuando no hay posiciones"""
    st.info("""
    👋 **¡Bienvenido a Portfolio Manager!**
    
    Aún no tienes posiciones en tu portfolio. Ve a la sección **Mi Portfolio** para agregar tu primera inversión.
    """)

def show_main_metrics(metrics, currency="USD"):
    """Mostrar métricas principales del portfolio"""
    
    currency_symbol = "$" if currency == "USD" else "$"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Capital Invertido</div>
            <div class="metric-value">{currency_symbol}{metrics['total_invested']:,.2f}</div>
            <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;">{currency}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Valor Actual</div>
            <div class="metric-value">{currency_symbol}{metrics['total_value']:,.2f}</div>
            <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;">{currency}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pnl_class = "positive" if metrics['total_pnl'] >= 0 else "negative"
        pnl_symbol = "▲" if metrics['total_pnl'] >= 0 else "▼"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ganancia/Pérdida</div>
            <div class="metric-value">{currency_symbol}{metrics['total_pnl']:,.2f}</div>
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
    
    tickers = [p['ticker'] for p in positions_detail]
    values = [p['current_value'] for p in positions_detail]
    
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
    
    df = pd.DataFrame(positions_detail)
    df = df.sort_values('pnl_pct', ascending=True)
    
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

def show_positions_summary(positions_detail, currency="USD"):
    """Mostrar tabla resumida de posiciones"""
    
    st.markdown("### 💼 Resumen de Posiciones")
    
    if not positions_detail:
        st.info("No hay posiciones para mostrar")
        return
    
    df = pd.DataFrame(positions_detail)
    
    # Crear listas para cada columna con formato y color
    data_rows = []
    
    for _, row in df.iterrows():
        # Determinar color del P&L
        pnl_color = "🟢" if row['pnl'] >= 0 else "🔴"
        
        data_rows.append({
            'Ticker': row['ticker'],
            'Moneda': row['currency'],
            'Cantidad': f"{row['quantity']:.4f}",
            'Precio Compra': f"${row['purchase_price']:.2f} {row['currency']}",
            'Precio Actual': f"${row['current_price']:.2f} {row['currency']}",
            f'Valor ({currency})': f"${row['current_value']:,.2f}",
            f'P&L ({currency})': f"{pnl_color} ${row['pnl']:,.2f}",
            'P&L %': f"{pnl_color} {row['pnl_pct']:+.2f}%",
            'Dist.': f"{row['allocation']:.1f}%"
        })
    
    display_df = pd.DataFrame(data_rows)
    
    st.dataframe(display_df, use_container_width=True, height=400)

def convert_metrics_to_ars(metrics: dict, usd_ars_rate: float) -> dict:
    """
    Convertir todas las métricas de USD a ARS
    
    Args:
        metrics: Diccionario con métricas en USD
        usd_ars_rate: Tasa de cambio USD/ARS
        
    Returns:
        dict: Métricas convertidas a ARS
    """
    converted = metrics.copy()
    
    # Convertir totales
    converted['total_invested'] = metrics['total_invested'] * usd_ars_rate
    converted['total_value'] = metrics['total_value'] * usd_ars_rate
    converted['total_pnl'] = metrics['total_pnl'] * usd_ars_rate
    # El porcentaje se mantiene igual
    
    # Convertir detalles de cada posición
    converted_details = []
    for detail in metrics['positions_detail']:
        converted_detail = detail.copy()
        converted_detail['invested'] = detail['invested'] * usd_ars_rate
        converted_detail['current_value'] = detail['current_value'] * usd_ars_rate
        converted_detail['pnl'] = detail['pnl'] * usd_ars_rate
        # pnl_pct y allocation se mantienen igual
        converted_details.append(converted_detail)
    
    converted['positions_detail'] = converted_details
    
    return converted
