"""
Análisis Técnico - Indicadores y gráficos
"""

import streamlit as st
from utils.database import get_user_positions
from utils.market_data import get_technical_indicators, interpret_rsi, interpret_macd, interpret_sma, interpret_bollinger
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show(supabase, user):
    """Mostrar página de análisis técnico"""
    
    st.markdown("# 📈 Análisis Técnico")
    st.markdown("Indicadores técnicos avanzados para tus inversiones")
    
    # Obtener posiciones del usuario
    positions = get_user_positions(supabase, user['id'])
    
    if not positions:
        st.info("No tienes posiciones para analizar. Agrega posiciones en la sección Mi Portfolio.")
        return
    
    # Selector de ticker
    tickers = sorted(list(set([p['ticker'] for p in positions])))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_ticker = st.selectbox(
            "Selecciona un activo para analizar",
            tickers,
            format_func=lambda x: f"📊 {x}"
        )
    
    with col2:
        period = st.selectbox(
            "Período de análisis",
            ["1mo", "3mo", "6mo", "1y", "2y"],
            index=3,
            format_func=lambda x: {
                "1mo": "1 mes",
                "3mo": "3 meses",
                "6mo": "6 meses",
                "1y": "1 año",
                "2y": "2 años"
            }.get(x, x)
        )
    
    if not selected_ticker:
        return
    
    # Obtener indicadores técnicos
    with st.spinner(f"Calculando indicadores para {selected_ticker}..."):
        indicators = get_technical_indicators(selected_ticker, period)
    
    if not indicators:
        st.error("No se pudieron obtener los datos. Verifica que el ticker sea correcto.")
        return
    
    # Mostrar indicadores principales
    show_indicators_summary(selected_ticker, indicators)
    
    st.markdown("---")
    
    # Gráficos detallados
    show_price_chart(selected_ticker, indicators)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_rsi_chart(selected_ticker, indicators)
    
    with col2:
        show_macd_chart(selected_ticker, indicators)

def show_indicators_summary(ticker, indicators):
    """Mostrar resumen de indicadores"""
    
    st.markdown(f"### 📊 Indicadores de {ticker}")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Precio actual
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Precio Actual</div>
            <div class="metric-value">${indicators['current_price']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # RSI
    with col2:
        rsi_interp = interpret_rsi(indicators['rsi'])
        rsi_color = {
            'sobrecompra': '#ef4444',
            'sobreventa': '#10b981',
            'neutral': '#f59e0b'
        }.get(rsi_interp['signal'], '#6b7280')
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">RSI (14)</div>
            <div class="metric-value" style="color: {rsi_color}">{indicators['rsi']:.1f}</div>
            <div class="metric-change" style="color: {rsi_color}; font-size: 0.75rem;">{rsi_interp['signal'].upper()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # MACD
    with col3:
        macd_interp = interpret_macd(indicators['macd']['macd'], indicators['macd']['signal'])
        macd_color = '#10b981' if macd_interp['signal'] == 'alcista' else '#ef4444'
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">MACD</div>
            <div class="metric-value" style="color: {macd_color}">{indicators['macd']['macd']:.2f}</div>
            <div class="metric-change" style="color: {macd_color}; font-size: 0.75rem;">{macd_interp['signal'].upper()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # SMA 50
    with col4:
        sma_50 = indicators['sma_50']
        sma_trend = "▲" if indicators['current_price'] > sma_50 else "▼"
        sma_color = '#10b981' if indicators['current_price'] > sma_50 else '#ef4444'
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SMA 50</div>
            <div class="metric-value">${sma_50:.2f}</div>
            <div class="metric-change" style="color: {sma_color};">{sma_trend}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # SMA 200
    with col5:
        sma_200 = indicators['sma_200']
        trend_200 = "▲" if indicators['current_price'] > sma_200 else "▼"
        trend_color = '#10b981' if indicators['current_price'] > sma_200 else '#ef4444'
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SMA 200</div>
            <div class="metric-value">${sma_200:.2f}</div>
            <div class="metric-change" style="color: {trend_color};">{trend_200}</div>
        </div>
        """, unsafe_allow_html=True)

def show_price_chart(ticker, indicators):
    """Mostrar gráfico de precio con Bandas de Bollinger y SMAs"""
    
    st.markdown("### 📈 Gráfico de Precio y Bandas de Bollinger")
    
    data = indicators['data']
    
    # Crear figura
    fig = go.Figure()
    
    # Bandas de Bollinger
    fig.add_trace(go.Scatter(
        x=data.index,
        y=indicators['bollinger_bands']['series']['upper'],
        name='BB Superior',
        line=dict(color='rgba(124, 58, 237, 0.3)', width=1, dash='dash'),
        fill=None
    ))
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=indicators['bollinger_bands']['series']['lower'],
        name='BB Inferior',
        line=dict(color='rgba(124, 58, 237, 0.3)', width=1, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(124, 58, 237, 0.1)'
    ))
    
    # SMA 50 y 200
    fig.add_trace(go.Scatter(
        x=data.index,
        y=indicators['series']['sma_50'],
        name='SMA 50',
        line=dict(color='#f59e0b', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=indicators['series']['sma_200'],
        name='SMA 200',
        line=dict(color='#ef4444', width=2)
    ))
    
    # Precio de cierre
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Precio',
        line=dict(color='#00d4aa', width=3)
    ))
    
    # Layout
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 31, 46, 0.5)',
        font=dict(color='white', family='Sora'),
        xaxis=dict(
            gridcolor='#2d3748',
            showgrid=True,
            title=''
        ),
        yaxis=dict(
            gridcolor='#2d3748',
            showgrid=True,
            title='Precio ($)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_rsi_chart(ticker, indicators):
    """Mostrar gráfico de RSI"""
    
    st.markdown("### 📊 RSI (Relative Strength Index)")
    
    data = indicators['data']
    rsi = indicators['series']['rsi']
    
    fig = go.Figure()
    
    # Línea de RSI
    fig.add_trace(go.Scatter(
        x=data.index,
        y=rsi,
        name='RSI',
        line=dict(color='#00d4aa', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 170, 0.2)'
    ))
    
    # Líneas de referencia
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", opacity=0.5, 
                  annotation_text="Sobrecompra (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981", opacity=0.5,
                  annotation_text="Sobreventa (30)")
    fig.add_hline(y=50, line_dash="dot", line_color="#6b7280", opacity=0.3)
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 31, 46, 0.5)',
        font=dict(color='white', family='Sora'),
        xaxis=dict(gridcolor='#2d3748', showgrid=True, title=''),
        yaxis=dict(gridcolor='#2d3748', showgrid=True, title='RSI', range=[0, 100]),
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_macd_chart(ticker, indicators):
    """Mostrar gráfico de MACD"""
    
    st.markdown("### 📊 MACD (Moving Average Convergence Divergence)")
    
    data = indicators['data']
    macd = indicators['macd']['series']['macd']
    signal = indicators['macd']['series']['signal']
    histogram = indicators['macd']['series']['histogram']
    
    # Crear subplots
    fig = make_subplots(rows=2, cols=1, 
                        row_heights=[0.7, 0.3],
                        vertical_spacing=0.05,
                        shared_xaxes=True)
    
    # MACD y Signal lines
    fig.add_trace(go.Scatter(
        x=data.index, y=macd,
        name='MACD',
        line=dict(color='#00d4aa', width=2)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=data.index, y=signal,
        name='Signal',
        line=dict(color='#ef4444', width=2)
    ), row=1, col=1)
    
    # Histogram
    colors = ['#10b981' if val >= 0 else '#ef4444' for val in histogram]
    fig.add_trace(go.Bar(
        x=data.index, y=histogram,
        name='Histogram',
        marker=dict(color=colors)
    ), row=2, col=1)
    
    # Layout
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 31, 46, 0.5)',
        font=dict(color='white', family='Sora'),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    fig.update_xaxes(gridcolor='#2d3748', showgrid=True)
    fig.update_yaxes(gridcolor='#2d3748', showgrid=True)
    
    st.plotly_chart(fig, use_container_width=True)
