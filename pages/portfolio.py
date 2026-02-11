"""
Portfolio - Gestión de posiciones
"""

import streamlit as st
from utils.database import (get_user_positions, add_position, update_position, 
                            delete_position, calculate_portfolio_metrics)
from utils.market_data import get_current_price, get_stock_info, detect_currency, convert_to_usd
from datetime import datetime, date
import pandas as pd

def show(supabase, user):
    """Mostrar página de gestión de portfolio"""
    
    st.markdown("# 💼 Mi Portfolio")
    st.markdown("Gestiona tus posiciones de inversión")
    
    tab1, tab2 = st.tabs(["📋 Ver Posiciones", "➕ Agregar Posición"])
    
    with tab1:
        show_positions(supabase, user)
    
    with tab2:
        add_new_position(supabase, user)

def show_positions(supabase, user):
    """Mostrar y gestionar posiciones existentes"""
    
    positions = get_user_positions(supabase, user['id'])
    
    if not positions:
        st.info("No tienes posiciones en tu portfolio. Agrega una nueva posición usando la pestaña de arriba.")
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
    
    # Mostrar cada posición con opciones de edición
    st.markdown("### Tus Posiciones")
    
    for detail in metrics['positions_detail']:
        with st.expander(f"**{detail['ticker']}** - ${detail['current_value']:,.2f} USD", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Información de la Posición")
                st.markdown(f"**Cantidad:** {detail['quantity']:.4f}")
                st.markdown(f"**Precio de Compra:** ${detail['purchase_price']:.2f} {detail['currency']}")
                st.markdown(f"**Precio Actual:** ${detail['current_price']:.2f} {detail['currency']}")
                st.markdown(f"**Fecha de Compra:** {detail['purchase_date']}")
            
            with col2:
                st.markdown("#### 💰 Rendimiento (en USD)")
                st.markdown(f"**Invertido:** ${detail['invested']:,.2f} USD")
                st.markdown(f"**Valor Actual:** ${detail['current_value']:,.2f} USD")
                
                pnl_color = "green" if detail['pnl'] >= 0 else "red"
                st.markdown(f"**P&L:** :{pnl_color}[${detail['pnl']:,.2f} ({detail['pnl_pct']:.2f}%)]")
                st.markdown(f"**Distribución:** {detail['allocation']:.1f}%")
            
            st.markdown("---")
            
            # Opciones de eliminación
            if st.button(f"🗑️ Eliminar {detail['ticker']}", key=f"delete_{detail['id']}", use_container_width=True):
                if delete_position(supabase, detail['id']):
                    st.success(f"Posición {detail['ticker']} eliminada correctamente")
                    st.rerun()

def add_new_position(supabase, user):
    """Formulario para agregar nueva posición"""
    
    st.markdown("### Agregar Nueva Posición")
    st.markdown("Ingresa los detalles de tu nueva inversión")
    
    # Tabs con ejemplos por tipo
    with st.expander("📚 Ejemplos de Tickers por Categoría", expanded=False):
        tab1, tab2, tab3 = st.tabs(["🇺🇸 USA", "🇦🇷 Argentina", "🌎 CEDEARs"])
        
        with tab1:
            st.markdown("""
            ### Acciones USA y ADRs
            
            **Tech:**
            - `AAPL` - Apple
            - `MSFT` - Microsoft
            - `GOOGL` - Google
            - `TSLA` - Tesla
            - `NVDA` - Nvidia
            
            **ADRs Latinoamericanos:**
            - `MELI` - MercadoLibre
            - `GLOB` - Globant
            - `DESP` - Despegar
            
            ✅ **No llevan sufijo**
            """)
        
        with tab2:
            st.markdown("""
            ### Acciones Argentinas
            
            **Energía:**
            - `YPFD.BA` - YPF
            - `PAMP.BA` - Pampa Energía
            - `TGSU2.BA` - TGS
            
            **Bancos:**
            - `GGAL.BA` - Grupo Galicia
            - `BMA.BA` - Banco Macro
            - `SUPV.BA` - Supervielle
            
            **Otras:**
            - `TXAR.BA` - Ternium
            - `COME.BA` - Comercial del Plata
            - `CRES.BA` - Cresud
            
            ⚠️ **Siempre agregar `.BA`**
            """)
        
        with tab3:
            st.markdown("""
            ### CEDEARs (Acciones USA en Argentina)
            
            **Tech:**
            - `AAPL.BA` - Apple CEDEAR
            - `MSFT.BA` - Microsoft CEDEAR
            - `GOOGL.BA` - Google CEDEAR
            - `TSLA.BA` - Tesla CEDEAR
            
            **Otras:**
            - `KO.BA` - Coca-Cola CEDEAR
            - `DIS.BA` - Disney CEDEAR
            - `NFLX.BA` - Netflix CEDEAR
            
            ⚠️ **CEDEARs también llevan `.BA`**
            
            💡 **Diferencia:** Un CEDEAR es una acción USA que cotiza en Argentina en pesos.
            """)
    
    with st.form("add_position_form", clear_on_submit=True):
